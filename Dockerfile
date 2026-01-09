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
        libpq5 \
        postgresql-common \
        make \
        rsync \
    && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y \
    && apt-get install --assume-yes --no-install-recommends \
        postgresql-client-17 \
    && apt-get distclean

ARG DEPENDENCY_GROUPS=prod
ARG BUILD_DEPENDENCIES="g++ gcc libc6-dev libpq-dev zlib1g-dev"

# uv settings
# https://github.com/astral-sh/uv-docker-example/blob/main/pyproject.toml
# https://hynek.me/articles/docker-uv/

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Silence uv complaining about not being able to use hard links.
ENV UV_LINK_MODE=copy
# https://github.com/astral-sh/uv/pull/6834#issuecomment-2319253359
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
ENV UV_PYTHON_PREFERENCE=only-system

# https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
# uv version can not be defined in an environment variable,
# because COPY --from doesn't support variable expansion
# https://github.com/moby/moby/issues/34482
COPY --from=ghcr.io/astral-sh/uv:0.9.22@sha256:2320e6c239737dc73cccce393a8bb89eba2383d17018ee91a59773df802c20e6 /uv /uvx /bin/

# install python dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    apt-get update \
    && apt-get install --assume-yes --no-install-recommends ${BUILD_DEPENDENCIES} \
    && uv sync --frozen --no-install-project --group ${DEPENDENCY_GROUPS} \
    && apt-get purge --assume-yes --auto-remove ${BUILD_DEPENDENCIES} \
    && apt-get distclean

# copy project
COPY . .

RUN python -m django compilemessages --ignore .venv

# ENTRYPOINT is specified only in the local docker-compose.yml to avoid
# accidentally running it in deployed environments.
