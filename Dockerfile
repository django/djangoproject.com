# pull official base image
FROM python:3.12-slim-trixie

# set work directory
WORKDIR /usr/src/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install deb packages
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends \
        gettext \
        git \
        make \
        rsync \
    && apt-get distclean

ARG REQ_FILE=requirements/prod.txt

# install python dependencies
COPY ./requirements ./requirements
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends \
        g++ \
        gcc \
    && python3 -m pip install --no-cache-dir -r ${REQ_FILE} \
    && apt-get purge --assume-yes --auto-remove \
        g++ \
        gcc \
    && apt-get distclean

# copy project
COPY . .

RUN python -m django compilemessages

# ENTRYPOINT is specified only in the local docker-compose.yml to avoid
# accidentally running it in deployed environments.
