collectstatics: compile-scss
	./manage.py collectstatic --noinput

compile-scss:
	compass compile --sass-dir static/scss --css-dir static/css -e production --no-sourcemap --force

compile-scss-debug:
	compass compile --sass-dir static/scss --css-dir static/css -e development --sourcemap --force

