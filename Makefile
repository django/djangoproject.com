STATIC = djangoproject/static
JQUERY_FLOT=djangoproject/static/js/lib/jquery-flot

.PHONY: collectstatics compile-scss compile-scss-debug watch-scss run install test ci

collectstatics: compile-scss
	./manage.py collectstatic --noinput

compile-scss:
	compass compile --sass-dir $(STATIC)/scss --css-dir $(STATIC)/css -e production --no-sourcemap --force

compile-scss-debug:
	compass compile --sass-dir $(STATIC)/scss --css-dir $(STATIC)/css -e development --sourcemap --force

watch-scss:
	compass watch --sass-dir $(STATIC)/scss --css-dir $(STATIC)/css -e production --no-sourcemap --force

run:
	python manage.py runserver 0.0.0.0:8000

install:
	pip install -r requirements/dev.txt

test:
	@coverage run manage.py test -v2 aggregator contact docs fundraising legacy releases svntogit

ci: test
	@coverage report

$(JQUERY_FLOT)/jquery.flot.min.js: $(JQUERY_FLOT)
	cat $(JQUERY_FLOT)/jquery.flot.js $(JQUERY_FLOT)/jquery.flot.time.js > $(JQUERY_FLOT)/jquery.flot.concat.js
	yuicompressor $(JQUERY_FLOT)/jquery.flot.concat.js -o $(JQUERY_FLOT)/jquery.flot.min.js

$(JQUERY_FLOT)/:
	bower install
