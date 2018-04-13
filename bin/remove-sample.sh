#! /bin/bash

set -eou pipefail

# Grab environment variables
. ./.env

if [ -f manage.py ]; then rm manage.py; fi
rm -rf dead_songs
rm -rf api

if [ -f ./Backups/dead_songs.sql ]; then rm ./Backups/dead_songs.sql; fi

# remove sample database
docker-compose -f development-docker-compose.yml run api_development /bin/bash -c "export PGPASSWORD=${DEVELOPMENT_POSTGRES_PASSWORD}; psql -h "$DEVELOPMENT_POSTGRES_HOST" -U "$DEVELOPMENT_POSTGRES_USER" -c 'DROP DATABASE IF EXISTS dead_songs'; unset PGPASSWORD"

