djangoproject.com source code
=============================

.. image:: https://github.com/django/djangoproject.com/workflows/Tests/badge.svg?branch=main
    :target: https://github.com/django/djangoproject.com/actions

.. image:: https://coveralls.io/repos/django/djangoproject.com/badge.svg?branch=main
    :target: https://coveralls.io/r/django/djangoproject.com?branch=main

To run locally, you can either:

- Install and run from a virtual environment
- Run with docker compose (see below)

Install and run locally from a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Create a `Python Python 3.12 virtualenv and activate it <https://docs.python.org/3/library/venv.html>`_

#. Install dependencies::

    python3 -m pip install -r requirements/dev.txt

   Alternatively, use the make task::

    make install

#. Make a directory to store the project's data (``MEDIA_ROOT``, ``DOC_BUILDS_ROOT``,
   etc.). We'll use ``~/.djangoproject`` for example purposes. Create a sub-directory
   named ``conf`` inside that directory::

    mkdir -p ~/.djangoproject/conf

   Create a ``secrets.json`` file in the ``conf`` directory, containing something
   like::

    {
      "secret_key": "xyz",
      "superfeedr_creds": ["any@email.com", "some_string"],
      "db_host": "localhost",
      "db_password": "secret",
      "db_user": "djangoproject",
      "trac_db_host": "localhost",
      "trac_db_password": "secret",
      "trac_db_user": "code.djangoproject"
    }

#. Add ``export DJANGOPROJECT_DATA_DIR=~/.djangoproject`` (without the backticks)
   to your ``~/.bashrc`` (or ``~/.zshrc`` if you're using zsh, ``~/.bash_profile`` if
   you're on macOS and using bash) file and then run ``source ~/.bashrc`` (or
   ``source ~/.zshrc``, or ``source ~/.bash_profile``) to load the changes.

#. Create databases::

    createuser -d djangoproject --superuser
    createdb -O djangoproject djangoproject
    createuser -d code.djangoproject --superuser
    createdb -O code.djangoproject code.djangoproject

#. Setting up database access

   If you are using the default postgres configuration, chances are you will
   have to give a password for the newly created users to be able to
   use them for Django::

     psql
     ALTER USER djangoproject WITH PASSWORD 'secret';
     ALTER USER "code.djangoproject" WITH PASSWORD 'secret';
     \d

   (Use the same passwords as the ones you've used in your ``secrets.json`` file)

#. Create tables::

    psql -d code.djangoproject < tracdb/trac.sql

    python -m manage migrate

#. Create a superuser::

    python -m manage createsuperuser

#. Populate the www and docs hostnames in the django.contrib.sites app::

    python -m manage loaddata dev_sites

#. For docs (next step requires ``gettext``)::

    python -m manage loaddata doc_releases
    python -m manage update_docs --update-index

#. For dashboard:

   To load the latest dashboard categories and metrics::

    python -m manage loaddata dashboard_production_metrics

   Alternatively, to load a full set of sample data (takes a few minutes)::

    python -m manage loaddata dashboard_example_data

   Finally, make sure the loaded metrics have at least one data point (this
   makes API calls to the URLs from the metrics objects loaded above and may
   take some time depending on the metrics chosen)::

    python -m manage update_metrics

#. Compile the CSS (only the source SCSS files are stored in the repository)::

    make compile-scss

#. Finally, run the server::

    make run

   This runs both the main site ("www") as well as the
   docs and dashboard site in the same process.
   Open http://www.djangoproject.localhost:8000/,
   http://docs.djangoproject.localhost:8000/,
   or http://dashboard.djangoproject.localhost:8000/.

Running the tests
-----------------

We use GitHub actions for continuous testing and
`GitHub <https://github.com/>`_ pull request integration. If you're familiar
with those systems you should not have any problems writing tests.

Our test results can be found here:

* https://github.com/django/djangoproject.com/actions

For local development don't hesitate to install
`tox <https://tox.readthedocs.io/>`_ to run the website's test suite.

Then in the root directory (next to the ``manage.py`` file) run::

    tox

Behind the scenes, this will run the usual ``python -m manage test`` management
command with a preset list of apps that we want to test. We
collect test coverage data as part of that tox run, to show the result
simply run::

    python -m coverage report

or for a HTML-based report::

    python -m coverage html

**(Optional)** In case you're using an own virtualenv you can also run the
tests manually using the ``test`` task of the ``Makefile``. Don't forget to
install the test requirements with the following command first though::

    python -m pip install -r requirements/tests.txt

Then run::

    make test

or simply the usual test management command::

    python -m manage test [list of app labels]

Supported browsers
------------------

The goal of the site is to target various levels of browsers, depending on
their ability to use the technologies in use on the site, such as HTML5, CSS3,
SVG, webfonts.

We're following `Mozilla's example <https://wiki.mozilla.org/Support/Browser_Support>`_
when it comes to categorizing browser support.

- Desktop browsers, except as noted below, are **A grade**, meaning that
  everything needs to work.

- IE < 11 is **not supported** (based on Microsoft's support).

- Mobile browsers should be considered **B grade** as well.
  Mobile Safari, Firefox on Android and the Android Browser should support
  the responsive styles as much as possible but some degradation can't be
  prevented due to the limited screen size and other platform restrictions.

File locations
--------------

Static files such as CSS, JavaScript or image files can be found in the
``djangoproject/static`` subdirectory.

Templates can be found in the ``djangoproject/templates`` subdirectory.

Styles
------

CSS is written in `Scss <http://sass-lang.com/>`_ and compiled via
`Libsass <https://sass-lang.com/libsass/>`_.

Run the following to compile the Scss files to CSS::

    make compile-scss-debug

Alternatively, you can also run the following command in a separate shell
to continuously watch for changes to the Scss files and automatically compile
to CSS::

    make watch-scss

Running all at once
-------------------

Optionally you can use a tool like `Foreman <https://github.com/ddollar/foreman>`_
to run all process at once:

- the site (similar to www.djangoproject.com) on http://0.0.0.0:8000/ to be used
  with the modified /etc/hosts file (see above)
- the ``make`` task to automatically compile the SCSS files to CSS files

This is great during development. Assuming you're using Foreman simply run::

    foreman start

If you just want to run one of the processes defined above use the
``run`` subcommand like so::

    foreman run web

That'll just run the www server.

Check out the ``Procfile`` file for all the process names.

JavaScript libraries
--------------------

This project's JavaScript libraries can be found in
``djangoproject/static/js/lib/``. If you need to add a library, commit the
minified version of it to this directory.

Documentation search
--------------------

When running ``python -m manage update_docs --update-index`` to build all
documents it will also automatically index every document it builds in the
search engine as well. In case you've already built the documents and would like
to reindex the search index, run the command::

    python -m manage update_index

This is also the right command to run when you work on the search feature
itself. You can pass the ``-d`` option to try to drop the search index
first before indexing all the documents.

Updating metrics from production
--------------------------------

The business logic for dashboard metrics is edited via the admin interface and
contained in the models in the ``dashboard`` app (other than ``Dataum``, which
contains the data itself). From time to time, those metrics should be extracted
from a copy of the production database and saved to the
``dashboard/fixtures/dashboard_production_metrics.json`` file.

To update this file, run::

    python -m manage dumpdata dashboard --exclude dashboard.Datum --indent=4 > dashboard_production_metrics.json

Translation
-----------

We're using Transifex to help manage the translation process. The
Transifex client app is required. To install it, run::

    curl -o- https://raw.githubusercontent.com/transifex/cli/master/install.sh | bash

Before using the command-line Transifex client, create ``~/.transifexrc``
according to the instructions at
https://docs.transifex.com/client/client-configuration. You'll need to be a
member of the Django team in the `Django
<https://explore.transifex.com/django/>`_ organization at Transifex. For
information on how to join, please see the `Translations
<https://docs.djangoproject.com/en/dev/internals/contributing/localizing/#translations>`_
section of the documentation on contributing to and localizing Django.

Since this repo hosts three separate sites, our ``.po`` files are organized by
website domain. At the moment, we have:

* ``dashboard/locale/`` contains the translation files for
  https://dashboard.djangoproject.com
* ``docs/locale/`` contains the translation files for
  https://docs.djangoproject.com (only for the strings in this repository;
  translation of the documentation itself is handled elsewhere)
* ``locale/`` contains the translation files for https://www.djangoproject.com
  (including strings from all apps other than ``dashboard`` and ``docs``)

**Important:** To keep this working properly, note that any templates for the
``dashboard`` and ``docs`` apps **must** be placed in the
``<app name>/templates/<app name>/`` directory of the respective app, **not** in
the ``djangoproject/templates/`` directory.

Updating messages on Transifex
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When there are changes to the messages in the code or templates, a member of
the translations team will need to update Transifex as follows:

1. Regenerate the English (only) .po file::

    python -m manage makemessages -l en

   (Never update alternate language .po files using makemessages. We'll update
   the English file, upload it to Transifex, then later pull the .po files with
   translations down from Transifex.)

2. Push the updated source file to Transifex::

     tx push -s

3. Commit and push the changes to GitHub::

     git commit -m "Updated messages" locale/en/LC_MESSAGES/*
     git push

Updating translations from Transifex
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Anytime translations on Transifex have been updated, someone should update
our translation files as follows:

1. Review the translations in Transifex and add to the space-delimited
   ``LANGUAGES`` list in ``update-translations.sh``, any new languages that have
   reached 100% translation.

2. Pull the updated translation files::

    ./update-translations.sh

3. Use ``git diff`` to see if any translations have actually changed. If not,
   you can just revert the .po file changes and stop here.

4. Compile the messages::

    python -m manage compilemessages

5. Run the test suite one more time::

    python -m manage test

6. Commit and push the changes to GitHub::

    git commit -m "Updated translations" locale/*/LC_MESSAGES/*
    git push

Running Locally with Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Build the images::

    docker compose build

2. Spin up the containers::

    docker compose up

3. View the site at http://localhost:8000/

4. Run the tests::

    docker compose run --rm web tox
    docker compose run --rm web python -m manage test

Pre-commit checks
-----------------

`pre-commit <https://pre-commit.com>`_ is a framework for managing pre-commit
hooks. These hooks help to identify simple issues before committing code for
review. By checking for these issues before code review it allows the reviewer
to focus on the change itself, and it can also help to reduce the number of CI
runs.

To use the tool, first install ``pre-commit`` and then the git hooks

.. code-block:: console

    $ python3 -m pip install pre-commit
    $ python3 -m pre_commit install

On the first commit ``pre-commit`` will install the hooks, these are
installed in their own environments and will take a short while to
install on the first run. Subsequent checks will be significantly faster.
If the an error is found an appropriate error message will be displayed.
If the error was with ``isort`` then the tool will go ahead and fix them for
you. Review the changes and re-stage for commit if you are happy with
them.
