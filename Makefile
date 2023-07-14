STATIC = djangoproject/static
SCSS = djangoproject/scss
JQUERY_FLOT=djangoproject/static/js/lib/jquery-flot
APP_LIST ?= accounts aggregator blog contact dashboard djangoproject docs foundation fundraising legacy members releases svntogit tracdb

.PHONY: collectstatics compile-scss compile-scss-debug watch-scss run install test ci

collectstatics: compile-scss
	python -m manage collectstatic --noinput

compile-scss:
	pysassc $(SCSS)/output.scss $(STATIC)/css/output.css -s compressed

compile-scss-debug:
	pysassc $(SCSS)/output.scss $(STATIC)/css/output.css --sourcemap

watch-scss:
	watchmedo shell-command --patterns=*.scss --recursive --command="make compile-scss-debug" $(SCSS)

run:
	python -m manage runserver 0.0.0.0:8000

install:
	python -m pip install -r requirements/dev.txt
	npm install

migrations-check:
	python -m manage makemigrations --check --dry-run

test: migrations-check
	@python -m coverage run --source=. manage.py test -v2 $(APP_LIST)

ci: test
	@python -m coverage report

isort:
	python -m isort $(APP_LIST)

isort-check:
	python -m isort -c $(APP_LIST)

$(JQUERY_FLOT)/jquery.flot.min.js: $(JQUERY_FLOT)
	cat $(JQUERY_FLOT)/jquery.flot.js $(JQUERY_FLOT)/jquery.flot.time.js > $(JQUERY_FLOT)/jquery.flot.concat.js
	yuicompressor $(JQUERY_FLOT)/jquery.flot.concat.js -o $(JQUERY_FLOT)/jquery.flot.min.js

$(JQUERY_FLOT)/:
	npm run bower install
