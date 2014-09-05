To run locally, do the usual::

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

    ./manage.py syncdb
    ./manage.py migrate

   and::

    ./manage.py syncdb --docs
    ./manage.py migrate --docs

   if you want to run docs site.

6. For docs::

    ./manage.py loaddata doc_releases.json --docs
    ./manage.py update_docs --docs

Finally::

    ./manage.py runserver

This runs as ``www.djangoproject.com``. To run locally as
``docs.djangoproject.com``, use::

    ./manage.py runserver --docs
