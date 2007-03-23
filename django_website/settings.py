import os, platform

# Far too clever trick to know if we're running on the deployment server.
DEVELOPMENT_MODE = ("servers.ljworld.com" not in platform.node())

ADMINS = (('Adrian Holovaty','holovaty@gmail.com'), ('Jacob Kaplan-Moss', 'jacob@lawrence.com'))
TIME_ZONE = 'America/Chicago'

SERVER_EMAIL = 'root@pam.servers.ljworld.com'
MANAGERS = (('Wilson Miner','wminer@ljworld.com'),)

if DEVELOPMENT_MODE:
    DEBUG = True
    PREPEND_WWW = False
    DATABASE_ENGINE = "sqlite3"
    DATABASE_NAME = "/tmp/djangoproject.db"
    CACHE_BACKEND = "file:///tmp/djangoprojectcache/"
    TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), "templates")]
    DJANGO_SVN_ROOT = "http://code.djangoproject.com/svn/django/"
else:
    DEBUG = False
    PREPEND_WWW = True
    DATABASE_ENGINE = 'postgresql'
    DATABASE_NAME = 'djangoproject'
    DATABASE_USER = 'apache'
    DATABASE_PASSWORD = ''
    DATABASE_HOST = '10.0.0.80' # set to empty string for localhost
    CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
    TEMPLATE_DIRS = ['/home/html/templates/djangoproject.com/']
    DJANGO_SVN_ROOT = "file:///home/svn/django/django/"

SITE_ID = 1
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
    'django.contrib.sitemaps',
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
USE_I18N = False

