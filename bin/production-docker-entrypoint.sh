#! /bin/bash

# wait-for-postgres.sh
# https://docs.docker.com/compose/startup-order/

set -eou pipefail

source /code/bin/get-ssm-parameters.sh

echo Debug: $DEBUG

./manage.py collectstatic --noinput

#python manage.py migrate

gunicorn $PROJECT_NAME.wsgi -c gunicorn_config.py
