#!/bin/sh

python -m manage migrate
make compile-scss # must come before collectstatic
python -m manage collectstatic --no-input --clear

exec "$@"
