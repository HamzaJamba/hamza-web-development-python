# Deploying to Azure

Target layout: three **Azure App Service (Linux, containers)** apps sharing one image registry, plus managed data services.

| Resource | Purpose | Suggested SKU |
|---|---|---|
| Azure Container Registry | `oilops-backend`, `oilops-web` images | Basic |
| App Service plan (Linux) | Hosts the three apps | B2 / P1v3 |
| Web App `oilops-api` | Gunicorn API (`oilops-backend`) | |
| Web App `oilops-worker` | `celery worker -B` (same image) | |
| Web App `oilops-web` | Nginx + React build (`oilops-web`) | |
| Azure Database for PostgreSQL Flexible Server | Primary database | Burstable B2s |
| Azure Cache for Redis | Cache, throttling, Celery broker | Basic C0 |
| Azure Storage (Blob) | Optional: uploaded media | |

## 1. Provision

```bash
RG=oilops-rg; LOC=uaenorth; ACR=oilopsacr$RANDOM; PLAN=oilops-plan
az group create -n $RG -l $LOC
az acr create -g $RG -n $ACR --sku Basic
az appservice plan create -g $RG -n $PLAN --is-linux --sku B2
for APP in oilops-api oilops-worker oilops-web; do
  az webapp create -g $RG -p $PLAN -n $APP --container-image-name $ACR.azurecr.io/oilops-backend:latest
  az webapp identity assign -g $RG -n $APP
done
az postgres flexible-server create -g $RG -n oilops-pg --tier Burstable --sku-name Standard_B2s --version 16 \
  --admin-user oilops --admin-password '<strong-password>' --database-name oilops --public-access 0.0.0.0
az redis create -g $RG -n oilops-redis --sku Basic --vm-size c0 -l $LOC
```

Let each web app pull from ACR with its managed identity: grant the identity the `AcrPull` role on the registry and set `acrUseManagedIdentityCreds=true`.

## 2. Configure app settings

Set on `oilops-api` and `oilops-worker` (the worker also gets `RUN_MIGRATIONS=0`):

```
DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=<random 50+ chars>
ALLOWED_HOSTS=oilops-api.azurewebsites.net
CORS_ALLOWED_ORIGINS=https://oilops-web.azurewebsites.net
CSRF_TRUSTED_ORIGINS=https://oilops-api.azurewebsites.net
DATABASE_URL=postgres://oilops:<pw>@oilops-pg.postgres.database.azure.com:5432/oilops?sslmode=require
REDIS_URL=rediss://:<access-key>@oilops-redis.redis.cache.windows.net:6380/0
SECURE_SSL_REDIRECT=True
COOKIE_SECURE=True
HSTS_SECONDS=31536000
IOT_DEVICE_API_KEY=<random>
WEBSITES_PORT=8000
WEBSITES_ENABLE_APP_SERVICE_STORAGE=true     # persists /app/media; prefer Blob Storage for production
```

`oilops-web` needs `WEBSITES_PORT=80` and `API_UPSTREAM=https://oilops-api.azurewebsites.net` is **not** used when the SPA is built with an absolute API URL (see below).

## 3. GitHub Actions (OIDC, no stored passwords)

1. Create an Entra ID app registration, add a **federated credential** for your repository (`environment:production`), and grant it `Contributor` on the resource group and `AcrPush` on the registry.
2. In the repository set **secrets** `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` and **variables** `ACR_NAME`, `AZURE_API_APP`, `AZURE_WORKER_APP`, `AZURE_WEB_APP`, `API_PUBLIC_URL`.
3. Push to `main`. `CI` runs tests and builds; on success `Deploy to Azure` pushes both images, rolls out the three apps, then calls `/api/health/`.

The SPA image is built with `VITE_API_URL=$API_PUBLIC_URL/api/v1`, so the browser talks to the API app directly (CORS is configured above).

## 4. First release

```bash
az webapp ssh -g $RG -n oilops-api         # or use the Kudu console
python manage.py createsuperuser
python manage.py seed_demo                  # optional demo data
```

Migrations and `collectstatic` run automatically at API container start (`scripts/entrypoint.sh`).

## 5. Operations checklist

* Turn on Application Insights for the three apps; alert on 5xx rate and on `/api/health/` failures.
* Enable PostgreSQL automated backups and test a restore.
* Scale the worker independently; keep a single `-B` (beat) instance, or move beat to its own app when you scale workers out.
* Rotate `SECRET_KEY` and the device key through Key Vault references (`@Microsoft.KeyVault(...)`) in app settings.
