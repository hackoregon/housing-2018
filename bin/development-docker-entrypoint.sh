#! /bin/bash

# wait-for-postgres.sh
# https://docs.docker.com/compose/startup-order/

set -eou pipefail

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -p "$POSTGRES_PORT" -d postgres -c '\q'
do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up"

echo Debug: $DEBUG

# Collect static files
echo "Collect static files"
./manage.py collectstatic --noinput

echo "Make migrations"
./manage.py makemigrations

echo "Migrate"
./manage.py migrate

echo "Load data"
./manage.py shell --command="import data.loader"

echo "Create Postgres backup file"
PGPASSWORD=$POSTGRES_PASSWORD pg_dump -Fp -v -C -c -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -p "$POSTGRES_PORT" $POSTGRES_NAME > ./Backups/$POSTGRES_NAME.sql

# or load from backup if we want instead
#PGPASSWORD=$POSTGRES_PASSWORD psql < ./$POSTGRES_NAME.sql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres

echo "Run server..."
./manage.py runserver 0.0.0.0:8000
