# from worldonline.settings.default import *

ADMINS = (('Adrian Holovaty','holovaty@gmail.com'), ('Jacob Kaplan-Moss', 'jacob@lawrence.com'))
TIME_ZONE = 'America/Chicago'

SERVER_EMAIL = 'root@pam.servers.ljworld.com'
MANAGERS = (('Wilson Miner','wminer@ljworld.com'),)

DEBUG = False
PREPEND_WWW = True

DATABASE_ENGINE = 'postgresql'
DATABASE_NAME = 'djangoproject'
DATABASE_USER = 'apache'
DATABASE_PASSWORD = ''
DATABASE_HOST = '10.0.0.80' # set to empty string for localhost

SITE_ID = 1
TEMPLATE_DIRS = (
    '/home/html/templates/djangoproject.com/',
    '/home/html/templates/default/',
)
ROOT_URLCONF = 'django_website.urls'
INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django_website.apps.blog',
    'django_website.apps.docs',
    'django_website.apps.aggregator',
)
ADMIN_MEDIA_PREFIX = 'http://media.djangoproject.com/admin/'
MEDIA_ROOT = "/home/html/djangoproject.com/m/"
MEDIA_URL = "http://www.djangoproject.com.com/m/"

# setting for documentation root path
DJANGO_DOCUMENT_ROOT_PATH = "/home/html/djangoproject.com/docs/"
DJANGO_TESTS_PATH = "/home/html/djangoproject.com/tests/"

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 1 # 1 hour
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangoproject'
CACHE_MIDDLEWARE_GZIP = True

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
