FROM postgres:16

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-16-cron \
        postgresql-16-partman && \
    rm -rf /var/lib/apt/lists/*

RUN echo "shared_preload_libraries = 'pg_cron,pg_partman_bgw'" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "cron.database_name = 'postgres'" >> /usr/share/postgresql/postgresql.conf.sample \
