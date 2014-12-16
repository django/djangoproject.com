djangoproject.com source code
=============================

To run locally, do the usual:

1. Create a virtualenv

2. Install dependencies::

    pip install -r deploy-requirements.txt
    pip install -r local-requirements.txt

   If you only need to deploy, and don't need to test any changes,
   you can use deploy-requirements.txt only.

3. Create a 'secrets.json' file in the directory above the checkout, containing
   something like::

    { "secret_key": "xyz",
      "superfeedr_creds": ["any@email.com", "some_string"] }

4. Create databases::

    createuser -d djangoproject
    createdb -O djangoproject djangoproject
    createuser code.djangoproject
    createdb -O code.djangoproject code.djangoproject

5. Create tables::

    psql -d code.djangoproject < tracdb/trac.sql

    ./manage.py migrate

   and::

    ./manage.py migrate --docs

   if you want to run docs site.

6. For docs::

    ./manage.py loaddata doc_releases.json --docs
    ./manage.py update_docs --docs

7. Finally::

    ./manage.py runserver

   This runs as ``www.djangoproject.com``, the main website.

   To run locally as ``docs.djangoproject.com``, use::

    ./manage.py runserver --docs

Styles
------

In case you want to work on the stylesheets please install
`Compass <http://compass-style.org/>`_ with
`Rubygems <http://rubygems.org/>`_::

    gem install compass

You may have to prefix that command with ``sudo`` depending on your platform.

Then run the following to compile the Compass SASS files to CSS::

    make compile-scss-debug

Alternatively you can also run the following command in a separate shell
to continously watch for changes to the SASS files and automatically compile
to CSS::

    make watch-scss
