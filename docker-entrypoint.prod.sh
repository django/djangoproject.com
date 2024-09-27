#!/bin/sh

python -m manage migrate
python -m manage compilemessages
make compile-scss # must come before collectstatic
python -m manage collectstatic --no-input --clear

exec "$@"
