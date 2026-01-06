#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

until pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done

echo "PostgreSQL is ready"

# TEMPORARY DEBUG: Check the contents of the versions directory
echo "Listing contents of the migration versions directory:"
ls -F /app/app/alembic/versions

echo "Running database migrations..."
alembic -c alembic.ini upgrade head

echo "Waiting for DDL commands to commit (5 seconds)..."
sleep 5

# ... rest of the script ...
echo "Creating default superuser..."
python /app/scripts/create_superuser.py

echo "Starting application..."
exec "$@"
