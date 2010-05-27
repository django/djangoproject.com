import os, platform

BASE = os.path.abspath(os.path.dirname(__file__))

# Far too clever trick to know if we're running on the deployment server.
DEVELOPMENT_MODE = (platform.node() != "djangoproject")

ADMINS = (('Adrian Holovaty','holovaty@gmail.com'), ('Jacob Kaplan-Moss', 'jacob@jacobian.org'))
TIME_ZONE = 'America/Chicago'

SERVER_EMAIL = 'root@djangoproject.com'
MANAGERS = (('Jacob Kaplan-Moss','jacob@jacobian.org'),)

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'djangoproject'
TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), "templates")]

if DEVELOPMENT_MODE:
    DEBUG = True
    PREPEND_WWW = False
    CACHE_BACKEND = "dummy:///"
    DJANGO_SVN_ROOT = "http://code.djangoproject.com/svn/django/"
    MEDIA_ROOT = os.path.abspath(os.path.join(BASE, '..', 'media'))
    MEDIA_URL = "/media/"
    ADMIN_MEDIA_PREFIX = '/admin_media/'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    DEBUG = False
    PREPEND_WWW = True
    DATABASE_USER = 'apache'
    CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
    TEMPLATE_DIRS = ['/home/djangoproject.com/django_website/templates']
    DJANGO_SVN_ROOT = "file:///home/svn/django/django/"
    MEDIA_ROOT = "/home/html/djangoproject.com/m/"
    MEDIA_URL = "http://www.djangoproject.com.com/m/"
    ADMIN_MEDIA_PREFIX = 'http://media.djangoproject.com/admin/'

SITE_ID = 1
ROOT_URLCONF = 'django_website.urls'
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
    'registration',
)

# setting for documentation root path
DJANGO_DOCUMENT_ROOT_PATH = "/home/html/djangoproject.com/docs/"
DJANGO_TESTS_PATH = "/home/html/djangoproject.com/tests/"

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

USE_I18N = False

DEFAULT_FROM_EMAIL = "noreply@djangoproject.com"

# django-registration settings
ACCOUNT_ACTIVATION_DAYS = 3

# comment_utils settings
AKISMET_API_KEY = "c892e4962244"
