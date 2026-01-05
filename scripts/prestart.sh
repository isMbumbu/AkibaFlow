#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

until pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done

echo "PostgreSQL is ready"

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
