# Settings for www.djangoproject.com

from django_www.common_settings import *


### Django settings

ALLOWED_HOSTS = ['www.djangoproject.com', 'djangoproject.com']

CACHE_MIDDLEWARE_KEY_PREFIX = 'djangoproject'

DATABASES['trac'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'code.djangoproject',
    'USER': 'code.djangoproject'
}

DATABASE_ROUTERS = ['tracdb.db_router.TracRouter']

PREPEND_WWW = PRODUCTION

ROOT_URLCONF = 'django_www.urls'

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_push.subscriber',

    'djangosecure',
    'registration',
    'south',

    'accounts',
    'aggregator',
    'blog',
    'cla',
    'contact',
    'docs',             # provides the DocumentRelease model used in the tests
    'legacy',
    'releases',
    'svntogit',
    'tracdb',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'docs.context_processors.docs_version',
    'releases.context_processors.django_version',
]


### django-contact-form / Akismet settings

AKISMET_API_KEY = "c892e4962244"


### django-registration settings

ACCOUNT_ACTIVATION_DAYS = 3


### aggregator / PubSubHubbub settings

FEED_APPROVERS_GROUP_NAME = "feed-approver"

PUSH_HUB = 'https://superfeedr.com/hubbub'
PUSH_CREDENTIALS = 'aggregator.utils.push_credentials'
PUSH_SSL_CALLBACK = PRODUCTION
# SUPERFEEDR_CREDS is a 2 element list in the form of [email,secretkey]
SUPERFEEDR_CREDS = SECRETS.get('superfeedr_creds')


### South settings

SOUTH_TESTS_MIGRATE = False


### Enable optional components

if DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        INSTALLED_APPS.append('debug_toolbar')
        INTERNAL_IPS = ['127.0.0.1']
        MIDDLEWARE_CLASSES.insert(
            MIDDLEWARE_CLASSES.index('django.middleware.common.CommonMiddleware') + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware')

# Log errors to Sentry instead of email, if available.
if 'sentry_dsn' in SECRETS:
    INSTALLED_APPS.append('raven.contrib.django')
    SENTRY_DSN = SECRETS['sentry_dsn']
    LOGGING["loggers"]["django.request"]["handlers"].remove("mail_admins")
