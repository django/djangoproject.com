djangoproject.com source code
=============================

To run locally, do the usual:

#. Create a virtualenv

#. Install dependencies::

    pip install -r deploy-requirements.txt
    pip install -r local-requirements.txt

   If you only need to deploy, and don't need to test any changes,
   you can use deploy-requirements.txt only.

#. Create a 'secrets.json' file in the directory above the checkout, containing
   something like::

    { "secret_key": "xyz",
      "superfeedr_creds": ["any@email.com", "some_string"] }

#. Create databases::

    createuser -d djangoproject
    createdb -O djangoproject djangoproject
    createuser code.djangoproject
    createdb -O code.djangoproject code.djangoproject

#. Set debug environment variable::

    export DJANGOPROJECT_DEBUG=1

   The code of the project uses this env variable to distinguish between
   production and development. Set it to ``1`` to disable settings that are only
   relevant on the production server.

#. Create tables::

    psql -d code.djangoproject < tracdb/trac.sql

    ./manage.py migrate

   and::

    ./manage.py migrate --docs

   if you want to run docs site.

#. For docs::

    ./manage.py loaddata doc_releases.json --docs
    ./manage.py update_docs --docs

#. Finally::

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

Running all at once
-------------------

Optionally you can use a tool like `Foreman <https://github.com/ddollar/foreman>`_
to run all process at once:

- the regular site (similar to www.djangoproject.com) on http://127.0.0.1:8000/
- the docs site (similar to docs.djangoproject.com) on port http://127.0.0.1:8001/
- the ``make`` task to automatically compile the SASS files to CSS files

This is great during development. Assuming you're using Foreman simply run::

  foreman start

If you just want to run one of the processes defined above use the
``run`` subcommand like so::

  foreman run www

That'll just run the www server.

Check out the ``Procfile`` file for all the process names.
