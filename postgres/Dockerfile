FROM postgres:16-alpine

RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    postgresql-contrib \
    && apk add --no-cache \
    postgresql-plpython3 \
    && apk add --no-cache postgresql-server-dev-all \
    && apk add --no-cache postgresql-plpython3

RUN apk add --no-cache pg_partman && apk add --no-cache postgresql-plpython3
RUN apk add --no-cache pg_cron && apk add --no-cache postgresql-plpython3

COPY ./init_pg_partman.sql /docker-entrypoint-initdb.d/
