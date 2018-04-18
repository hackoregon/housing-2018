# Housing Affordability 2018

## Goal
Synthesize complex information to understand the state of housing market and promote a vision for long-term affordability.

## About this Repository
The housing-2018 repository contains a Django Rest Framework-based API for serving up housing-related data. The API runs in Docker and is based on the example API from https://github.com/hackoregon/backend-examplar-2018. Separate from this API, the branch `elastic-exploration` contains a Docker-based Elasticsearch and Kibana environment for exploring housing-related data. This system was used at the beginning of the project and may be phased out as we focus on the Django API.

## API
This API provides access to all of the data contained in the Harvard Joint Center for Housing Studies 2017 State of the Nation's Housing report appendix tables. You can view all data by going to /housing/api/harvardjchs/, or filter by various values. To see all possible options, view the schema at /housing/schema/, or browse the possible filters from /housing/api/harvardjchs/meta/.

## Running locally
To run the API:
1. Clone the repo: `git clone https://github.com/hackoregon/housing-2018.git`
2. Create a `.env` file in the root folder based on `env.sample`. This can be easily done by `cp env.sample .env`. Make sure to change the Django Secret Key and Postgres password for any versions that will be on the internet.
3. Build the development containers by running `./bin/build.sh -d`. The -d flag builds the development version and it will run `docker-compose` with `development-docker-compose.yml`. The other option is `-p` for production. If you do not have permission to run, run `chmod +x bin/build.sh` to allow execution.
4. Start the project by running `./bin/start.sh -d` which will run `docker-compose up` using the `development-docker-compose.yml` file. Once these containers are up and running you can access the Swagger schema site at `http://localhost:8000/housing/schema`.

## Generating database restore files
The current operating procedure for Hack Oregon projects is to have each project generate a SQL file containing a backup/restore of the full DRF database (with data) that will feed the API. This file will then be loaded into the production database on AWS. You can generate this file by running all of the Django migrations and loading all of the data into the development database and then running `pg_dump` with options `-Fp -v -C -c` enabled in order to get the proper commands included. See https://www.postgresql.org/docs/9.6/static/app-pgdump.html for details on these options.

We have setup the development container to automatically generate this backup once it has finished loading the data into the development database, and it saves the file in the Backups folder with the file name being the name of the database.

We will add more details about the development process and how to contribute to this project as the process is hashed out in `https://github.com/hackoregon/backend-examplar-2018`.
