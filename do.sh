#!/bin/bash

COLUMNS="`tput cols`"
LINES="`tput lines`"
BOLD=$(tput bold)
NORMAL=$(tput sgr0)

PROJECT_IP="127.0.0.1"
PROJECT_HOSTS=(
    "dashboard.djangoproject.com"
    "dopcs.djangoproject.com"
    "www.djangoproject.com"
)

EXPOSE_PORTS=${EXPOSE_PORTS:-1}

COMPOSE_FILES="-f docker-compose.yml"

DOCKER_COMPOSE="docker compose ${COMPOSE_FILES}"

hosts() {
    for host in "${PROJECT_HOSTS[@]}"; do
        echo "$PROJECT_IP  $host"
    done
}


# Game-specific commands:
_requires() {
    service="$1"
    $DOCKER_COMPOSE ps -q $service &> /dev/null
    if [[ "$?" == 1 ]]; then
        echo "'$service' service is not running. Please run \`start\` first."
        exit 1
    fi
}

build() {
    $DOCKER_COMPOSE build --force-rm "${@:3}"
}

compose() {
    $DOCKER_COMPOSE "$@"
}

start() {
    $DOCKER_COMPOSE "$@" up
}

stop() {
    $DOCKER_COMPOSE down "$@"
}

shell() {
    _requires web
    exec web /bin/bash
}

migrate() {
    _requires web
    exec web ./manage.py migrate "$@"
}

makemigrations() {
    _requires web
    exec -w /usr/src/app web python -m django makemigrations "$@"
}

exec() {
    $DOCKER_COMPOSE exec -e COLUMNS -e LINES "$@"
}

$*
