STATIC = djangoproject/static

.PHONY: collectstatics compile-scss compile-scss-debug watch-scss run upgrade

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
	pip install -r deploy-requirements.txt
	pip install -r local-requirements.txt
