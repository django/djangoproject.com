#!/bin/sh

python -m manage flush --no-input
# PGPASSWORD=djangoproject psql --host db --port 5432 --username=code.djangoproject --dbname=code.djangoproject < tracdb/trac.sql
python -m manage migrate
make compile-scss # must come before collectstatic
python -m manage collectstatic --no-input --clear
python -m manage loaddata dev_sites
python -m manage loaddata doc_releases
# git config --global url."https://".insteadOf git://
# python -m manage update_docs
python -m manage loaddata dashboard_production_metrics
# python -m manage loaddata dashboard_example_data
python -m manage update_metrics
#python -m manage update_index

exec "$@"
