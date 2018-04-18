#! /bin/bash

# wait-for-postgres.sh
# https://docs.docker.com/compose/startup-order/

set -eou pipefail

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -p "$POSTGRES_PORT" -d "$POSTGRES_NAME" -c '\q'
do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up"

echo Debug: $DEBUG

./manage.py collectstatic --noinput

python manage.py migrate

gunicorn $PROJECT_NAME.wsgi -c gunicorn_config.py
