# Settings for www.djangoproject.com

import os
import platform
from unipath import FSPath as Path

# The full path to the django_website directory.
BASE = Path(__file__).absolute().ancestor(2)

# Far too clever trick to know if we're running on the deployment server.
PRODUCTION = ('DJANGOPROJECT_DEBUG' not in os.environ) and ("djangoproject" in platform.node())

ADMINS = (('Adrian Holovaty','holovaty@gmail.com'),('Jacob Kaplan-Moss', 'jacob@jacobian.org'))
MANAGERS = (('Jacob Kaplan-Moss','jacob@jacobian.org'),)
TIME_ZONE = 'America/Chicago'
SERVER_EMAIL = 'root@djangoproject.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangoproject',
        'USER': 'djangoproject'
    }
}

USE_I18N = False
USE_L10N = False

TEMPLATE_DIRS = [BASE.child('templates')]
MEDIA_ROOT = BASE.parent.child('media')

if PRODUCTION:
    DEBUG = False
    PREPEND_WWW = True
    CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
    MEDIA_URL = "http://www.djangoproject.com.com/m/"
    ADMIN_MEDIA_PREFIX = "http://www.djangoproject.com.com/m/admin/"
else:
    DEBUG = True
    PREPEND_WWW = False
    CACHE_BACKEND = "dummy:///"
    MEDIA_URL = "/media/"
    ADMIN_MEDIA_PREFIX = '/admin_media/'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_ID = 1
ROOT_URLCONF = 'django_website.urls.www'
INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django_website.blog',
    'django_website.aggregator',
    'django_website.docs',
    'registration',
)

CACHE_MIDDLEWARE_SECONDS = 60 * 5 # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangoproject'
CACHE_MIDDLEWARE_GZIP = True
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
]


DEFAULT_FROM_EMAIL = "noreply@djangoproject.com"

# django-registration settings
ACCOUNT_ACTIVATION_DAYS = 3

# comment_utils settings
AKISMET_API_KEY = "c892e4962244"

# setting for documentation root path
DJANGO_DOCUMENT_ROOT_PATH = "/home/html/djangoproject.com/docs/"
DJANGO_TESTS_PATH = "/home/html/djangoproject.com/tests/"

# XXX What's this for?
DJANGO_SVN_ROOT = "http://code.djangoproject.com/svn/django/"
