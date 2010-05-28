from django_website.settings.www import *

PREPEND_WWW = False
APPEND_SLASH = True
INSTALLED_APPS = ['django_website.docs']
TEMPLATE_CONTEXT_PROCESSORS += ["django.core.context_processors.request"]
ROOT_URLCONF = 'django_website.urls.docs'
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangodocs'

# Where to store the build Sphinx docs.
if DEVELOPMENT_MODE:
    DOCS_BUILD_ROOT = '/tmp/djangodocs'
else:
    DOCS_BUILD_ROOT = "/home/djangodocs/"