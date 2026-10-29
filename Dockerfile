# pull official base image
FROM python:3.12-slim-trixie

# set work directory
WORKDIR /usr/src/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade to a pip version that bundles a secure `certifi`.
# https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576
RUN python -m pip install "pip @ https://files.pythonhosted.org/packages/3f/06/3e4420302363fbb71be3c7f35ce042f54bfca330e3e66b3a2e3c4cca579f/pip-26.2.2-py3-none-any.whl#sha256=fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"

# install deb packages
# PostgreSQL dependencies are needed for dbshell and backup process
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends \
        gettext \
        git \
        postgresql-common \
        make \
        rsync \
    && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y \
    && apt-get install --assume-yes --no-install-recommends \
        postgresql-client-17 libpq5 \
    && apt-get distclean

ARG REQ_FILE=requirements/prod.txt
ARG BUILD_DEPENDENCIES="g++ gcc libc6-dev libpq-dev zlib1g-dev"

# install python dependencies
COPY ./requirements ./requirements
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends ${BUILD_DEPENDENCIES} \
    && python3 -m pip install --no-cache-dir -r ${REQ_FILE} \
    && if [ "${REQ_FILE}" = "requirements/tests.txt" ]; then \
        echo "Installing Playwright browsers..."; \
        python3 -m playwright install --with-deps chromium; \
    fi \
    && apt-get purge --assume-yes --auto-remove ${BUILD_DEPENDENCIES} \
    && apt-get distclean

# copy project
COPY . .

RUN python -m django compilemessages --ignore .venv

# ENTRYPOINT is specified only in the local docker-compose.yml to avoid
# accidentally running it in deployed environments.
