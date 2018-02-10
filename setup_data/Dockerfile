FROM python:3
WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY data-migrations.sh /usr/local/bin/data-migrations.sh
COPY ./data-migrations /usr/src/app/data-migrations
