# pull official base image
FROM python:3.12-slim-bookworm

# set work directory
WORKDIR /usr/src/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install deb packages
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends \
        gettext \
        git \
        libmemcached11 \
        libpq5 \
        make \
        netcat-openbsd \
        npm \
        postgresql-client-15 \
        rsync \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*

ARG REQ_FILE=requirements/prod.txt

# install python dependencies
COPY ./requirements ./requirements
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends \
        g++ \
        gcc \
        libc6-dev \
        libpq-dev \
        libmemcached-dev \
        zlib1g-dev \
    && python3 -m pip install --no-cache-dir -r ${REQ_FILE} \
    && apt-get purge --assume-yes --auto-remove \
        gcc \
        libc6-dev \
        libpq-dev \
        libmemcached-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# install node dependencies
COPY ./package.json ./package.json
RUN npm install

# copy project
COPY . .

# run docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.prod.sh"]
