from django_website.settings.www import *

PREPEND_WWW = False
APPEND_SLASH = True
TEMPLATE_CONTEXT_PROCESSORS += ["django.core.context_processors.request"]
ROOT_URLCONF = 'django_website.urls.docs'
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangodocs'

_has_ddt = 'debug_toolbar' in INSTALLED_APPS
INSTALLED_APPS = [
    'django_website.docs',
    'haystack',
]
if _has_ddt:
    INSTALLED_APPS.append('debug_toolbar')

# Where to store the build Sphinx docs.
if PRODUCTION:
    DOCS_BUILD_ROOT = BASE.ancestor(2).child('docbuilds')
else:
    DOCS_BUILD_ROOT = '/tmp/djangodocs'

# Haystack settings
HAYSTACK_SITECONF = 'django_website.docs.search_sites'
if PRODUCTION:
    HAYSTACK_SEARCH_ENGINE = 'xapian'
    HAYSTACK_XAPIAN_PATH = BASE.ancestor(2).child('djangodocs.index')
else:
    HAYSTACK_SEARCH_ENGINE = 'whoosh'
    HAYSTACK_WHOOSH_PATH = '/tmp/djangodocs.index'
