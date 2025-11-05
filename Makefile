.PHONY: all ci clean collectstatics compile-scss compile-scss-debug install run test watch-scss

APP_LIST ?= accounts aggregator blog contact dashboard djangoproject docs foundation fundraising legacy members releases svntogit tracdb
SCSS = djangoproject/scss
STATIC = djangoproject/static

ci: compilemessages test
	@uv run coverage report

compilemessages:
	uv run python manage.py compilemessages --ignore .venv

collectstatics: compile-scss
	uv run python manage.py collectstatic --noinput

compile-scss:
	uv run pysassc $(SCSS)/output.scss $(STATIC)/css/output.css --style=compressed

compile-scss-debug:
	uv run pysassc $(SCSS)/output.scss $(STATIC)/css/output.css --sourcemap

install:
	uv sync

migrations-check:
	uv run python manage.py makemigrations --check --dry-run

run:
	uv run python manage.py runserver 0.0.0.0:8000

test:
	@uv run coverage run --source=. --module manage test --verbosity 2 $(APP_LIST)

watch-scss:
	watchmedo shell-command --patterns=*.scss --recursive --command="make compile-scss-debug" $(SCSS)

reset-local-db:
	uv run python manage.py flush --no-input
	uv run python manage.py loaddata dev_sites
	uv run python manage.py loaddata doc_releases
	uv run python manage.py loaddata dashboard_production_metrics
	uv run python manage.py update_metrics
