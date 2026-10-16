.PHONY: up down seed test backend-test frontend-build logs schema postman
up:            ; docker compose up --build -d
down:          ; docker compose down
logs:          ; docker compose logs -f --tail=100
seed:          ; docker compose exec backend python manage.py seed_demo
simulate:      ; docker compose exec backend python manage.py simulate_iot --rounds 5 --spike-chance 0.1
backend-test:  ; cd backend && DJANGO_SETTINGS_MODULE=config.settings.test pytest
frontend-build: ; cd frontend && npm ci && npm run build
test: backend-test
schema:        ; cd backend && python manage.py spectacular --file ../docs/openapi.yml
postman: schema ; python backend/scripts/openapi_to_postman.py docs/openapi.yml postman/OilOps-Pro.postman_collection.json
