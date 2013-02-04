To run locally, do the usual::

1. Create a virtualenv::

    virtualenv .

2. Install dependencies::

    pip install -r deploy-requirements.txt

   If you only need to deploy, and don't need to test any changes,
   you can use local-requirements.txt

3. Set up your databases, as per django_website/settings/www.py

4. Install Trac::

    pip install trac==0.12
    trac-admin $DIRECTORY_OF_CHOICE initenv

   Enter in the appropriate info. If you're running PostgreSQL locally, a valid
   connection string would be `postgres://code.djangoproject@localhost/code.djangoproject`.

5. Create a 'secrets.json' file in the directoy above the checkout, containing
   something like::

    { "secret_key": "xyz",
      "superfeedr_creds": ["any@email.com", "some_string"] }

6. Sync and migrate your databases::

    ./manage.py syncdb --migrate

   and::

    ./manage.py syncdb --docs

   if you would like to run the docs site.

7. To install documentatin::

    ./manage.py loaddata doc_releases.json --docs
    ./manage.py update_docs --docs


Finally::

    ./manage.py runserver

This runs as ``www.djangoproject.com``. To run locally as
``docs.djangoproject.com``, use::

    ./manage.py runserver --settings=django_website.settings.docs
