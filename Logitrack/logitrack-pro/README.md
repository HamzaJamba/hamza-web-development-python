# LogiTrack Pro — Enterprise Logistics & Fleet Management Platform

Django + DRF backend simulating an enterprise logistics workflow (Aramco/DHL/Maersk-style).

## Modules built (ALL 25 roadmap modules covered)
- **accounts** — Custom User model (email login), Profile
- **authentication** — Register, Login (JWT), Refresh, Logout (blacklist), Profile, Change Password, Forgot/Reset Password, Email Verification
- **roles** — Separate Role & Permission system (Admin, Ops Manager, Warehouse Manager, Fleet Manager, Driver, Dispatcher, Viewer) + `HasRolePermission`
- **shipments** — Full lifecycle (draft → delivered), status history, attachments, tracking-number auto-gen
- **fleet** — Vehicles + maintenance records
- **drivers** — Driver profiles linked to vehicles
- **warehouses** — Warehouse + manager assignment
- **inventory** — Stock per warehouse, low-stock flag
- **routes** — Route planning (distance, time, toll)
- **incidents** — Accident/delay/breakdown reporting with photo upload
- **notifications** — Per-user notifications
- **tracking** — GPS live location logs + IoT sensor simulation (temperature-breach alerts) + WebSocket consumers (Django Channels) for live push
- **dashboard** — Summary cards + charts (monthly shipments, delivery success rate, vehicle utilization)
- **reports** — Shipment/Driver/Warehouse reports, exportable as CSV, Excel, or PDF
- **audit** — Every create/update/delete on core models (shipments, vehicles, drivers, warehouses, roles) logged with who/what/when/from-where; admin-only read API at `/api/audit/logs/`
- **API rate limiting** — DRF throttling: 10/min on login, 5/min on register & forgot-password, 1000/hr per authenticated user, 100/hr per anonymous IP
- **API docs** — Swagger UI (`/api/docs/`) and ReDoc (`/api/redoc/`) via drf-spectacular
- **Live Map** — `frontend/live_map.html`: Leaflet + OpenStreetMap page that shows all vehicles and updates live over WebSocket
- **Tests** — 19 passing tests: auth flow, shipment lifecycle, role/permission enforcement, audit logging, fleet validation, IoT alert logic
- **Docker** — Dockerfile + docker-compose (Postgres + Redis + Daphne ASGI) + nginx reverse-proxy config
- **CI/CD** — GitHub Actions workflow: migrate + test on push/PR, deploy stub for Azure on `main`
- **Professional GitHub docs** — `LICENSE` (MIT), `CONTRIBUTING.md`, `docs/ARCHITECTURE.md` (Mermaid diagram), `docs/ER_DIAGRAM.md` (Mermaid ERD), `docs/INSTALLATION.md`
- **Postman collection** — `postman_collection.json` covering every endpoint, with auto-saving auth token script

## Genuinely out of scope for a backend repo (needs external infra/your own accounts)
- Actually provisioning Azure App Service/PostgreSQL/Storage (infra-as-code is easy to add, but requires your Azure subscription/credentials to run)
- Real screenshots (needs a live deployed frontend to screenshot)
- Flutter driver app (explicitly "Future V2" in the original roadmap)

## Local Setup (SQLite, quick dev)

```bash
python -m venv venv
venv\Scripts\activate            # PowerShell: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py test            # optional: run test suite
daphne -b 0.0.0.0 -p 8000 config.asgi:application
# or for plain HTTP dev without WebSockets: python manage.py runserver
```

## Docker Setup (Postgres + Redis + full stack)

```bash
docker-compose up --build
```

## API Docs
- Swagger: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- Raw schema: `http://localhost:8000/api/schema/`

## WebSocket endpoints (live tracking)
- `ws://localhost:8000/ws/tracking/fleet/` — all vehicles' live GPS
- `ws://localhost:8000/ws/tracking/<vehicle_id>/` — one vehicle's live GPS

Posting a new GPS log via `POST /api/tracking/gps/` automatically broadcasts it to connected WebSocket clients.

## Key REST Endpoints

| Endpoint | Description |
|---|---|
| POST /api/auth/register/ | Register new user |
| POST /api/auth/login/ | Login (JWT access + refresh) |
| POST /api/auth/token/refresh/ | Refresh access token |
| POST /api/auth/logout/ | Logout (blacklists refresh token) |
| GET/PATCH /api/auth/profile/ | View/update own profile |
| POST /api/auth/change-password/ | Change password |
| POST /api/auth/forgot-password/ , /reset-password/ | Password reset flow |
| POST /api/auth/verify-email/ | Verify email with token |
| /api/roles/roles/, /api/roles/permissions/ | Role & permission CRUD (admin only) |
| /api/shipments/ + POST .../{id}/update-status/ | Shipment CRUD + status transitions |
| /api/fleet/vehicles/, /api/fleet/maintenance/ | Vehicle + maintenance CRUD |
| /api/drivers/ | Driver CRUD |
| /api/warehouses/ | Warehouse CRUD |
| /api/inventory/ | Inventory CRUD |
| /api/routes/ | Route CRUD |
| /api/incidents/ | Incident CRUD |
| /api/notifications/ | Per-user notifications |
| /api/tracking/gps/, /api/tracking/iot/ | GPS logs + IoT sensor readings |
| /api/dashboard/summary/, /charts/... | Dashboard cards + chart data |
| /api/reports/shipments/?format=pdf\|excel\|csv | Exportable reports |
| /api/audit/logs/ | Admin-only audit trail (who changed what, when) |

All endpoints except register/login/forgot-reset-password require `Authorization: Bearer <access_token>`.
