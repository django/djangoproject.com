from django_website.settings.www import *

PREPEND_WWW = False
APPEND_SLASH = True
TEMPLATE_CONTEXT_PROCESSORS += ["django.core.context_processors.request"]
ROOT_URLCONF = 'django_website.urls.docs'
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangodocs'

# Override INSTALLED_APPS so that we only have a few things running on docs.
# Keep around debug_toolbar and raven if the parent settings module installed
# them.
_new_apps = [
    'django_website.docs',
    'haystack',
]
if 'debug_toolbar' in INSTALLED_APPS:
    _new_apps.append('debug_toolbar')
if 'raven.contrib.django' in INSTALLED_APPS:
    _new_apps.append('raven.contrib.django')
INSTALLED_APPS = _new_apps

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
