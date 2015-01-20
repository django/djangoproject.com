djangoproject.com source code
=============================

To run locally, do the usual:

#. Create a virtualenv

#. Install dependencies::

    pip install -r requirements/dev.txt

   Alternatively use the make task::

    make install

#. Create a 'secrets.json' file in the directory above the checkout, containing
   something like::

    { "secret_key": "xyz",
      "superfeedr_creds": ["any@email.com", "some_string"] }

#. Create databases::

    createuser -d djangoproject
    createdb -O djangoproject djangoproject
    createuser code.djangoproject
    createdb -O code.djangoproject code.djangoproject

#. Create tables::

    psql -d code.djangoproject < tracdb/trac.sql

    ./manage.py migrate

#. Create a superuser::

   ./manage.py createsuperuser

#. Populate the www and docs hostnames in the django.contrib.sites app::

    ./manage.py loaddata dev_sites

#. For docs::

    ./manage.py loaddata doc_releases
    ./manage.py update_docs

#. Point the ``www.djangoproject.dev`` and ``docs.djangoproject.dev``
   hostnames with your ``/etc/hosts`` file to ``localhost``/``127.0.0.1``.
   Here's how it could look like::

     127.0.0.1  docs.djangoproject.dev, www.djangoproject.dev

   If you're on Mac OS and don't feel like editing the ``/etc/hosts`` file
   manually, there is a great preference pane called `Hosts.prefpane`_. On
   Ubuntu there is a `built-in network admin`_ GUI to do the same. Remember
   both require admin priviledges, just like you'd need when editing
   ``/etc/hosts`` with your favorite editor.

.. _`Hosts.prefpane`: https://github.com/specialunderwear/Hosts.prefpane
.. _`built-in network admin`: https://help.ubuntu.com/community/NetworkAdmin

#. Finally run the server::

    make run

   This runs both the main site ("www") as well as the
   docs site in the same process. Open http://www.djangoproject.dev:8000/
   or http://docs.djangoproject.dev:8000/.

Supported browsers
------------------

The goal of the site is to target various levels of browsers, depending on
their ability to use the technologies in use on the site, such as HTML5, CSS3,
SVG, webfonts.

We're following `Mozilla's example <https://wiki.mozilla.org/Support/Browser_Support>`_
when it comes to categorize browser support.

- Any browser other than IE8 and lower as **A grade**. Which means everything
  needs to work on those.

- IE8 is **B grade**, meaning that some functionality may be disabled, visual
  variations are acceptable but the content must work nevertheless.

- IE below 8 is **not supported**.

- Mobile browsers should be considered **B grade** as well.
  Mobile Safari, Firefox on Android and the Android Browser should support
  the responsive styles as much as possible but some degredation can't be
  prevented due to the limited screen size and other platform restrictions.

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

- the site (similar to www.djangoproject.com) on http://0.0.0.0:8000/ to be used
  with the modified /etc/hosts file (see above)
- the ``make`` task to automatically compile the SASS files to CSS files

This is great during development. Assuming you're using Foreman simply run::

  foreman start

If you just want to run one of the processes defined above use the
``run`` subcommand like so::

  foreman run web

That'll just run the www server.

Check out the ``Procfile`` file for all the process names.

JavaScript libraries
--------------------

This project uses `Bower <http://bower.io/>`_ for managing JS library
depedencies. See its documentation for how to use it. Here's the gist:

To update any of the dependencies, edit the ``bower.json`` file accordingly
and then run ``bower install`` to download the appropriate files to the
static directory. Commit the downloaded files to git (vendoring).
