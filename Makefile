.PHONY: all ci clean collectstatics compile-scss compile-scss-debug install run test watch-scss

APP_LIST ?= accounts aggregator blog contact dashboard djangoproject docs foundation fundraising legacy members releases svntogit tracdb
SCSS = djangoproject/scss
STATIC = djangoproject/static

ci: test
	@python -m coverage report

collectstatics: compile-scss
	python -m manage collectstatic --noinput

compile-scss:
	python -m pysassc $(SCSS)/output.scss $(STATIC)/css/output.css --style=compressed

compile-scss-debug:
	python -m pysassc $(SCSS)/output.scss $(STATIC)/css/output.css --sourcemap

install:
	python -m pip install --requirement requirements/dev.txt

isort:
	python -m isort $(APP_LIST)

isort-check:
	python -m isort --check $(APP_LIST)

migrations-check:
	python -m manage makemigrations --check --dry-run

run:
	python -m manage runserver 0.0.0.0:8000

test: migrations-check
	@python -m coverage run --source=. --module manage test --verbosity 2 $(APP_LIST)

watch-scss:
	watchmedo shell-command --patterns=*.scss --recursive --command="make compile-scss-debug" $(SCSS)
