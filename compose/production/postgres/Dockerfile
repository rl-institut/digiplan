FROM postgres:11.3

RUN apt-get update
RUN apt-get install -y postgresql-11-postgis-3

COPY ./compose/production/postgres/init.sql /docker-entrypoint-initdb.d/

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance \
