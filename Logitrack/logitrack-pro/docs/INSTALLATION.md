# Installation Guide

## Option A — Quick local dev (SQLite, no Docker)
```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
copy .env.example .env           # cp .env.example .env on macOS/Linux
python manage.py migrate
python manage.py createsuperuser
python manage.py test            # optional sanity check — should show "OK"
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```
Visit `http://127.0.0.1:8000/admin/` and `http://127.0.0.1:8000/api/docs/`.

## Option B — Full stack with Docker (Postgres + Redis)
```bash
docker-compose up --build
```
This starts Postgres, Redis, and the Django app together with the Redis-backed channel layer
(`USE_INMEMORY_CHANNEL_LAYER=False`), so WebSocket broadcasts work across multiple workers.

## Live Map (Leaflet)
Open `frontend/live_map.html` directly in a browser (or serve it with `python -m http.server`
from the `frontend/` folder). Paste a valid JWT access token (from `/api/auth/login/`) into the
"Token" field, then click Connect — it loads existing GPS logs and then listens on
`ws://<host>/ws/tracking/fleet/` for live pushes.

## Seeding roles (recommended after first migrate)
```bash
python manage.py shell
>>> from roles.models import Role
>>> for name, _ in Role.ROLE_CHOICES:
...     Role.objects.get_or_create(name=name)
```

## Running the test suite
```bash
python manage.py test
```
