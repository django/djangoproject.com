# pull official base image
FROM python:3.12-slim-trixie

# set work directory
WORKDIR /usr/src/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install deb packages
# PostgreSQL dependencies are needed for dbshell and backup process
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends \
        gettext \
        git \
        libatomic1 \
        libpq5 \
        postgresql-common \
        make \
        rsync \
    && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y \
    && apt-get install --assume-yes --no-install-recommends \
        postgresql-client-17 \
    && apt-get distclean

ARG REQ_FILE=requirements/prod.txt
ARG BUILD_DEPENDENCIES="g++ gcc libc6-dev libpq-dev zlib1g-dev"

# install python dependencies
COPY ./requirements ./requirements
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends ${BUILD_DEPENDENCIES} \
    && python3 -m pip install --no-cache-dir -r ${REQ_FILE} \
    && apt-get purge --assume-yes --auto-remove ${BUILD_DEPENDENCIES} \
    && apt-get distclean

# copy project
COPY . .

RUN python -m django compilemessages
RUN git config --global --add safe.directory /usr/src/app

# ENTRYPOINT is specified only in the local docker-compose.yml to avoid
# accidentally running it in deployed environments.
