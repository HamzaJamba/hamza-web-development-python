# OilOps Pro

Enterprise operations management for oil & gas companies. Not a CRUD demo: it simulates the daily loop of a real operator, from a sensor crossing a limit, through an auto-generated emergency work order, spare parts leaving stock, and the cost and downtime landing on the manager's dashboard.

| Layer | Stack |
|---|---|
| API | Python 3.12, Django 5, Django REST Framework, SimpleJWT, drf-spectacular |
| Data | PostgreSQL 16, Redis 7 (cache, throttling, Celery broker) |
| Async | Celery worker + Celery beat (scheduled jobs) |
| Web | React 18, TypeScript, Vite, Tailwind CSS 4, TanStack Query, Leaflet, Chart.js |
| Delivery | Docker, Docker Compose, Nginx, Gunicorn, GitHub Actions, Azure App Service |

## Quick start (Docker)

```bash
cp .env.example .env              # edit SECRET_KEY and passwords
docker compose up --build -d
docker compose exec backend python manage.py seed_demo
open http://localhost:8080
```

Demo logins (password `OilOps@2026!`): `admin@oilops.com`, `manager@oilops.com`, `engineer@oilops.com`, `tech1@oilops.com`, `safety@oilops.com`, `store@oilops.com`, `hr@oilops.com`, `viewer@oilops.com`.

Generate live telemetry (spikes trigger alerts, notifications and emergency work orders):

```bash
docker compose exec backend python manage.py simulate_iot --rounds 10 --interval 2 --spike-chance 0.1
```

| URL | What |
|---|---|
| http://localhost:8080 | Web app |
| http://localhost:8080/api/docs/ | Swagger UI |
| http://localhost:8080/api/redoc/ | ReDoc |
| http://localhost:8080/api/health/ | Health check |

## Local development (no Docker)

```bash
# backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.dev     # SQLite, tasks run inline, no Redis needed
python manage.py migrate && python manage.py seed_demo
python manage.py runserver

# frontend (second terminal)
cd frontend && npm install && npm run dev              # http://localhost:5173, proxies /api to :8000
```

Hot-reload stack with Postgres and Redis: `docker compose -f docker-compose.dev.yml up --build`.

## Modules

| Module | Highlights |
|---|---|
| Authentication | Email login, JWT access/refresh with rotation and blacklist on logout, 8 roles (RBAC), MFA fields reserved |
| Employees | Profile, department, position, shift, salary grade (HR-only), training records, certifications with expiry alerts |
| Plants | Plants, refineries, terminals, gas stations with map coordinates; pipelines; storage tanks with fill level |
| Equipment | Pump, compressor, valve, generator, turbine, sensor. Serial, status, purchase, warranty, last service, next maintenance, health score |
| Maintenance | Recurring plans per asset. Celery creates preventive work orders ahead of the due date, idempotently |
| Work orders | Preventive / corrective / emergency, priority, deadline, engineer + technicians, state machine, spare-part usage deducts stock, labour + parts cost |
| Incidents | Gas leak, fire, explosion, equipment failure, near miss, safety violation. Photo and document upload with type and size validation. Closing requires root cause. Equipment failure opens a repair work order |
| Inventory | Spare parts, chemicals, lubricants, safety equipment. Stock only changes via row-locked movements; low-stock alerts |
| IoT monitoring | Temperature, pressure, voltage, vibration, oil level. Warning and critical thresholds per category or per asset, alert de-duplication and escalation, auto-resolve, health scoring |
| Analytics | Equipment health, downtime, maintenance cost, incident rate, inventory usage, team performance |
| Notifications | In-app + email (async) for maintenance due, low stock, incidents, alerts, assignments |
| Reports | Maintenance, incident, equipment, monthly performance as JSON, PDF or Excel |
| Security | JWT, RBAC on every endpoint, audit log with before/after diffs, throttling (anon, user, login, ingest), upload validation, hardened production settings |

## Tests

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.test pytest --cov=apps
```

89 tests cover authentication, a role-by-endpoint permission matrix, the work order lifecycle, stock integrity, threshold/alert logic, incident rules, uploads, analytics, report exports, audit trail, notifications and rate limiting.

## Documentation

* `docs/ARCHITECTURE.md` - design decisions and data flow
* `docs/DEPLOYMENT.md` - Azure App Service step by step
* `docs/openapi.yml` - OpenAPI 3 schema
* `postman/` - Postman collection (152 requests, login script stores the token) and environment
