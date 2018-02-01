FROM python:3
WORKDIR /usr/src/app

COPY requirements.txt ./

ADD data-migrations.sh /usr/local/bin/data-migrations.sh
ADD ./data-migrations /usr/src/app/data-migrations
RUN pip install --no-cache-dir -r requirements.txt
