#!/bin/sh
set -e

echo "Running database migrations..."
cd /app
alembic -c apps/api/alembic.ini upgrade head || echo "Migration skipped (no revisions yet)"

echo "Starting backend server..."
exec uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000 --reload
