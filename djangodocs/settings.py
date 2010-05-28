from django_website.settings import *

PREPEND_WWW = False
APPEND_SLASH = True
INSTALLED_APPS = ['djangodocs']
TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), "templates")] + TEMPLATE_DIRS
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
]
    
ROOT_URLCONF = 'djangodocs.urls'
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangodocs'

# Where to store the build Sphinx docs.
if DEVELOPMENT_MODE:
    DOCS_BUILD_ROOT = '/tmp/djangodocs'
else:
    DOCS_BUILD_ROOT = "/home/djangodocs/"