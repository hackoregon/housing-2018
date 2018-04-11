#! /bin/bash

set -euo pipefail

if [ -z "${PROJECT_NAME:-}" ]; then
   . bin/set-env.sh 
fi

bin/remove-sample.sh

docker-compose -f development-docker-compose.yml run api_development django-admin.py startproject $PROJECT_NAME .

rm $PROJECT_NAME/settings.py
cp ./bin/example-settings.py $PROJECT_NAME/settings.py

sed -i '' 's/\<EXAMPLE_PROJECT_NAME\>/'$PROJECT_NAME'/g' $PROJECT_NAME/settings.py
