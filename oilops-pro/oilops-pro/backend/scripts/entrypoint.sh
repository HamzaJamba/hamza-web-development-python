#!/bin/sh
set -e
# Only the web container migrates / collects static; workers skip via RUN_MIGRATIONS=0
if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  echo "Waiting for database..."
  python - <<'PY'
import os, time, sys
import environ
from urllib.parse import urlparse
import socket
url = os.environ.get("DATABASE_URL", "")
if url.startswith("postgres"):
    u = urlparse(url)
    for _ in range(60):
        try:
            socket.create_connection((u.hostname, u.port or 5432), 2).close(); break
        except OSError:
            time.sleep(1)
    else:
        sys.exit("database unreachable")
PY
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
fi
exec "$@"
