# FactoryPulse — AI-Powered Industrial Equipment Monitoring & Predictive Maintenance

Factory floor machines (motors, compressors, conveyors, pumps, turbines, CNC mills) report
live sensor readings. A trained ML model flags anomalies in real time, a regression model
predicts when a machine will likely fail, and an LLM-backed assistant explains what's
happening in plain language for a maintenance engineer.

Django + DRF backend, React + Vite + Tailwind v4 + Framer Motion frontend.

## What makes this "AI", not just CRUD
- **`sensors/ml.py`** — trains a real `scikit-learn` `IsolationForest` per machine on its own
  reading history and uses it to score new readings as normal/anomalous. Falls back to
  configured safe-limits until a machine has enough history (25+ readings) to train on.
- **`maintenance/predict.py`** — fits a linear trend to recent vibration readings and
  projects forward to estimate Remaining Useful Life (hours/days until the safe limit is
  crossed) — a transparent, explainable model a maintenance team can actually trust.
- **`ai_assistant/services.py`** — builds a context summary (recent readings, anomalies,
  open work orders, RUL prediction) and asks an LLM (Claude or GPT, via `ANTHROPIC_API_KEY`
  / `OPENAI_API_KEY`) to explain it in plain language. With no API key set, it falls back
  to a rule-based summary built from the same data — fully demoable either way.

## Backend apps
accounts/authentication (JWT, email login), roles (Admin, Plant Manager, Maintenance
Engineer, Operator), equipment (machine registry), sensors (readings + anomaly detection +
WebSocket live push), maintenance (work orders + predictive maintenance), ai_assistant
(LLM explain endpoint), dashboard (OEE + plant overview + machine trend), audit (who
changed what, when).

**30 tests, all passing** — covering auth, roles/permissions, equipment, the anomaly
detector (including a real zero-variance vs. realistic-variance training scenario),
predictive maintenance (stable vs. degrading trends), the AI assistant's fallback path,
dashboard OEE math, and audit logging.

## Frontend pages
Auth, Dashboard (plant overview, OEE, live charts), Machines (list/filter), Machine Detail
(live sensor trend, AI assistant chat, predictive maintenance card), Work Orders.

## Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo       # 8 machines, 1600 historical readings, 2 work orders
python manage.py test            # optional — should show "OK" (30 tests)
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

Demo logins (password `Demo@12345`): `admin@factorypulse.io`, `manager@factorypulse.io`,
`engineer@factorypulse.io`, `operator@factorypulse.io`.

### Simulate live sensor data (for the WebSocket/live-chart demo)
```bash
python manage.py simulate_live
```
Keeps pushing new readings (with occasional injected anomalies) to all machines so the
live dashboard and charts have something to show in real time.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Opens on `http://localhost:5173`, proxying `/api/*` to `http://127.0.0.1:8000`.

### API docs
`http://127.0.0.1:8000/api/docs/` (Swagger) or `/api/redoc/`

### Enabling the real LLM assistant
Set `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`) in `backend/.env` and restart the server —
no code changes needed.
