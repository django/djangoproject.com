STATIC = djangoproject/static
JQUERY_FLOT=djangoproject/static/js/lib/jquery-flot

.PHONY: collectstatics compile-scss compile-scss-debug watch-scss run install test ci

collectstatics: compile-scss
	./manage.py collectstatic --noinput

compile-scss:
	sassc $(STATIC)/scss/output.scss $(STATIC)/css/output.css
	sassc $(STATIC)/scss/output-ie.scss $(STATIC)/css/output-ie.css

compile-scss-debug:
	sassc $(STATIC)/scss/output.scss $(STATIC)/css/output.css --sourcemap
	sassc $(STATIC)/scss/output-ie.scss $(STATIC)/css/output-ie.css --sourcemap

watch-scss:
	sassc -w $(STATIC)/scss/output.scss $(STATIC)/css/output.css --sourcemap

watch-scss-ie:
	sassc -w $(STATIC)/scss/output-ie.scss $(STATIC)/css/output-ie.css --sourcemap

run:
	python manage.py runserver 0.0.0.0:8000

install:
	pip install -r requirements/dev.txt

test:
	@coverage run manage.py test -v2 aggregator contact docs fundraising legacy releases svntogit dashboard

ci: test
	@coverage report

$(JQUERY_FLOT)/jquery.flot.min.js: $(JQUERY_FLOT)
	cat $(JQUERY_FLOT)/jquery.flot.js $(JQUERY_FLOT)/jquery.flot.time.js > $(JQUERY_FLOT)/jquery.flot.concat.js
	yuicompressor $(JQUERY_FLOT)/jquery.flot.concat.js -o $(JQUERY_FLOT)/jquery.flot.min.js

$(JQUERY_FLOT)/:
	bower install
