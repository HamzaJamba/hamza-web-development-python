# Contributing to LogiTrack Pro

Thanks for your interest in improving LogiTrack Pro.

## Development setup
```bash
git clone <repo-url>
cd logitrack-pro
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py test
```

## Branching
- `main` — production-ready code only
- `develop` — integration branch for the next release
- `feature/<name>` — one feature/module per branch, opened against `develop`

## Commit style
Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
Example: `feat(shipments): add status-history endpoint`

## Pull requests
1. Branch from `develop`.
2. Add/update tests for any behavior change — `python manage.py test` must pass.
3. Run `python manage.py makemigrations --check` to make sure no migration is missing.
4. Keep PRs scoped to one module/feature where possible.
5. Fill in the PR description: what changed, why, how it was tested.

## Code style
- Follow PEP 8; prefer explicit serializers/viewsets over shortcuts that hide behavior.
- New endpoints should be documented (drf-spectacular picks up docstrings automatically) and added to `postman_collection.json`.
- Any model touched by API writes should go through `AuditLogMixin` if it's a core business model (shipments, fleet, drivers, warehouses, roles).

## Reporting issues
Include: steps to reproduce, expected vs actual behavior, and relevant logs/tracebacks.
