#!/bin/bash

set -euo pipefail

es_url=http://elastic:${ELASTIC_PASSWORD}@elasticsearch:9200

# Wait for Elasticsearch to start up before doing anything.
until curl -s $es_url -o /dev/null; do
    sleep 1
done

for file in /usr/src/app/data-migrations/*.py
do
  filename="${file##*/}"
  echo "$filename"
  if [ ${filename:0:4} = 'skip' ]; then
    echo "Skipping $filename"
    continue
  fi
  dataset_name="${filename%.*}"
  response=$(curl --write-out %{http_code} --silent --output /dev/null $es_url/$dataset_name)
  echo "Looking for index $dataset_name"
  echo "Response: $response"
  if [ $response -eq 200 ]
  then
    echo "Skipping migration, index $dataset_name already exists."
  else
    echo "Running migration $file"
    python $file
#dt=`date`
#curl -XPOST $es_url/datasets/default -H 'Content-Type: application/json' -d '{ "ran": true, "lastUpdate": "'"$dt"'", "title": "jchs-data-2017", "description": "JCHS 2017 Appendix Tables", "source": "http://www.jchs.harvard.edu/sites/jchs.harvard.edu/files/all_son_2017_tables_current_6_12_17.xlsx" }'
  fi
done

