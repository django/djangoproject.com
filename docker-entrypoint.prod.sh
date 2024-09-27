#!/bin/sh

python manage.py migrate
make compile-scss # must come before collectstatic
python manage.py collectstatic --no-input --clear

exec "$@"
