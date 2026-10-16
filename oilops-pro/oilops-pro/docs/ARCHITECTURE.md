# Architecture

## Shape

```
React SPA ──► Nginx ──► Gunicorn / Django REST API ──► PostgreSQL
                              │  ▲
                              ▼  │
                 Redis ◄── Celery worker ◄── Celery beat (schedules)
IoT gateway ──(X-Device-Key)──► /monitoring/readings/
```

A modular monolith: one Django project, one app per business module under `backend/apps/`. Cross-module behaviour goes through small service functions (`services.py`), never through views calling each other.

## Key design decisions

**Business rules live in services, not serializers or views.** `workorders/services.py` owns the state machine (`start`, `hold`, `complete`, `cancel`, `assign`, `add_part`). Views translate HTTP; services enforce rules inside `transaction.atomic`. The same functions are used by Celery tasks, monitoring and incidents.

**Stock integrity.** `Item.quantity` is not writable through the API. `inventory.services.adjust_stock` locks the row (`select_for_update`), rejects negative balances, writes a `StockMovement` with `balance_after`, and fires a low-stock notification only on the transition into low stock.

**Alerts are signal, not noise.** `monitoring.services.ingest_reading` evaluates thresholds (equipment-specific limits override category limits), de-duplicates into one open alert per equipment and metric with an occurrence count, escalates warning to critical, and auto-resolves when readings return to normal. Health score is derived from open alerts and overdue maintenance. A critical alert can open an emergency work order (`AUTO_WORK_ORDER_ON_CRITICAL_ALERT`), once per asset.

**Idempotent scheduled jobs.** Celery beat jobs (preventive work order generation, maintenance reminders, low-stock sweep, certification expiry) check for existing open work or recent notifications first, so a retry or double run does nothing.

**RBAC in one place.** `core.permissions.RoleBasedPermission` is the default for the whole API. Each view declares `read_roles`, `write_roles` and optional `action_roles`. Default for writes is admin-only, so a forgotten declaration fails closed. Technicians may only act on work orders they are assigned to (checked in the service layer).

**Audit trail.** `AuditMixin` records create/update/delete with a field-level diff; login, failed login, logout, password change, report export, upload and work order transitions are logged explicitly. Admin-only read access.

**Device authentication.** Telemetry accepts either a user JWT or an `X-Device-Key` header for gateways. The key authenticates only the ingest endpoint (it maps to a pseudo-role with no other permissions).

**Analytics are DB-agnostic.** Monthly bucketing is done in Python over bounded ranges so the same code runs on PostgreSQL and SQLite (tests).

## Data model (core relations)

```
Plant 1─* Equipment 1─* WorkOrder *─* User(technicians)
  │            │  │            └─* SparePartUsage *─1 Item 1─* StockMovement
  │            │  └─* MaintenanceSchedule ──(generates)──► WorkOrder
  │            ├─* SensorReading, Alert, Threshold
  │            └─* Incident 1─* IncidentAttachment
  ├─* StorageTank, Pipeline(origin, destination)
  └─* Employee ─ Department / Position / Shift / SalaryGrade ─* Training, Certification
```

## Security notes

* Access tokens are 30 min, refresh tokens rotate and are blacklisted on logout.
* The SPA keeps tokens in `localStorage` for simplicity. For stricter environments move the refresh token to an `HttpOnly` cookie and add CSRF protection.
* Uploaded media is served by Nginx from a shared volume. For regulated data, put media behind authenticated download endpoints or Azure Blob Storage with SAS URLs.
* Set `SECRET_KEY`, DB password and `IOT_DEVICE_API_KEY` to strong unique values; enable `SECURE_SSL_REDIRECT`, `COOKIE_SECURE` and `HSTS_SECONDS` behind HTTPS.
* MFA: `mfa_enabled` / `mfa_secret` fields exist; TOTP enrolment and verification are the planned next step.

## Extending

Add a module: `startapp` under `apps/`, register in `INSTALLED_APPS` and `config/urls.py`, inherit `TimeStampedModel`, mix in `AuditMixin`, declare roles on the viewset, add tests to the permission matrix.
