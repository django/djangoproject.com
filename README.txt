To run locally, do the usual::

1. Create a virtualenv
2. Install dependencies::

    pip install -r deploy-requirements.txt

   If you only need to deploy, and don't need to test any changes,
   you can use local-requirements.txt

3. Set up databases, as per django_website/settings/www.py

4. Create a 'secrets.json' file in the directoy above the checkout, containing
   something like::

    { "secret_key": "xyz",
      "superfeedr_creds": ["any@email.com", "some_string"] }

5. Set up DB::

    ./manage.py syncdb
    ./manage.py migrate

   and::

    ./manage.py syncdb --docs

   if you want to run docs site.

6. For docs::

    ./manage.py loaddata doc_releases.json --docs
    ./manage.py update_docs --docs


Finally::

    python manage.py runserver

This runs as ``www.djangoproject.com``. To run locally as
``docs.djangoproject.com``, use::

    python manage.py runserver --settings=django_website.settings.docs
