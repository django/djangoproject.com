STATIC = djangoproject/static
SCSS = djangoproject/scss
JQUERY_FLOT=djangoproject/static/js/lib/jquery-flot
APP_LIST ?= accounts aggregator blog cla contact dashboard djangoproject docs fundraising legacy members releases svntogit tracdb

.PHONY: collectstatics compile-scss compile-scss-debug watch-scss run install test ci

collectstatics: compile-scss
	./manage.py collectstatic --noinput

compile-scss:
	sassc $(SCSS)/output.scss $(STATIC)/css/output.css -s compressed
	sassc $(SCSS)/output-ie.scss $(STATIC)/css/output-ie.css -s compressed

compile-scss-debug:
	sassc $(SCSS)/output.scss $(STATIC)/css/output.css --sourcemap
	sassc $(SCSS)/output-ie.scss $(STATIC)/css/output-ie.css --sourcemap

watch-scss:
	watchmedo shell-command --patterns=*.scss --recursive --command="make compile-scss-debug" $(SCSS)

run:
	python manage.py runserver 0.0.0.0:8000

install:
	pip install -r requirements/dev.txt
	npm install

test:
	@coverage run --source=. manage.py test -v2 $(APP_LIST)

ci: test
	@coverage report

isort:
	isort -rc $(APP_LIST)

isort-check:
	isort -c -rc $(APP_LIST)

$(JQUERY_FLOT)/jquery.flot.min.js: $(JQUERY_FLOT)
	cat $(JQUERY_FLOT)/jquery.flot.js $(JQUERY_FLOT)/jquery.flot.time.js > $(JQUERY_FLOT)/jquery.flot.concat.js
	yuicompressor $(JQUERY_FLOT)/jquery.flot.concat.js -o $(JQUERY_FLOT)/jquery.flot.min.js

$(JQUERY_FLOT)/:
	npm run bower install
