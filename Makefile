.PHONY: collectstatics compile-scss compile-scss-debug watch-scss run upgrade

collectstatics: compile-scss
	./manage.py collectstatic --noinput

compile-scss:
	compass compile --sass-dir static/scss --css-dir static/css -e production --no-sourcemap --force

compile-scss-debug:
	compass compile --sass-dir static/scss --css-dir static/css -e development --sourcemap --force

watch-scss:
	compass watch --sass-dir static/scss --css-dir static/css -e production --no-sourcemap --force

run:
	python manage.py runserver 0.0.0.0:8000

install:
	pip install -r deploy-requirements.txt
	pip install -r local-requirements.txt
