# Housing Affordability 2018

## Goal:
Synthesize complex information to understand the state of housing market and promote a vision for long-term affordability.

## About this Repository
The housing-2018 repository contains a Django Rest Framework-based API for serving up housing-related data. The API runs in Docker and is based on the example API from https://github.com/hackoregon/backend-examplar-2018. Separate from this API, the branch `elastic-exploration` contains a Docker-based Elasticsearch and Kibana environment for exploring housing-related data. This system was used at the beginning of the project and may be phased out as we focus on the Django API.

## Running locally
To run the API:
1. Clone the repo: `git clone https://github.com/hackoregon/housing-2018.git`
2. Create a `.env` file in the root folder based on `env.sample`. This can be easily done by `cp env.sample .env`. Make sure to change the Django Secret Key and Postgres password for any versions that will be on the internet.
3. Build the development containers by running `./bin/build.sh -l`. The -l flag indicates you are running this locally and it will run `docker-compose` with `development-docker-compose.yml`. The other options are `-s` for staging and `-t` for test. If you do not have permission to run, run `chmod +x bin/build.sh` to allow execution.
4. Start the project by running `./bin/start.sh -l` which will run `docker-compose up` using the `development-docker-compose.yml` file. Once this containers are up and running you can access the site at `http://localhost:8000/housing/schema`.

I will add more details about the development process and how to contribute to this project as the process is hashed out in `https://github.com/hackoregon/backend-examplar-2018`.
