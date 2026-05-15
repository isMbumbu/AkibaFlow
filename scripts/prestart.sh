#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

until pg_isready -h "${POSTGRES_SERVER:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER}"; do
  sleep 1
done

echo "PostgreSQL is ready"

echo "Running database migrations..."
alembic -c alembic.ini upgrade head

echo "Waiting for DDL commands to commit (5 seconds)..."
sleep 5

echo "Creating default superuser..."
python /app/scripts/create_superuser.py

echo "Starting application..."
exec "$@"
