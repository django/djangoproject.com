# Settings for www.djangoproject.com
import json

from unipath import FSPath as Path

# Utilities

# The full path to the repository root.
BASE = Path(__file__).absolute().ancestor(2)

# It's a secret to everybody
try:
    with open(BASE.ancestor(2).child('conf').child('secrets.json')) as handle:
        SECRETS = json.load(handle)
except IOError:
    SECRETS = {'secret_key': 'a', 'superfeedr_creds': ['any@email.com', 'some_string']}


# Django settings

CACHE_MIDDLEWARE_SECONDS = 60 * 5  # 5 minutes

CACHE_MIDDLEWARE_KEY_PREFIX = 'django'

CSRF_COOKIE_HTTPONLY = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangoproject',
        'USER': 'djangoproject',
        'HOST': SECRETS.get('db_host', ''),
        'PASSWORD': SECRETS.get('db_password', ''),
    },
    'trac': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'code.djangoproject',
        'USER': 'code.djangoproject',
        'HOST': SECRETS.get('trac_db_host', ''),
        'PASSWORD': SECRETS.get('trac_db_password', ''),
    }
}

DATABASE_ROUTERS = ['tracdb.db_router.TracRouter']

DEFAULT_FROM_EMAIL = "noreply@djangoproject.com"

FIXTURE_DIRS = [BASE.child('fixtures')]

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
    'haystack',
    'registration',
    'django_pygments',
    'django_hosts',

    'accounts',
    'aggregator',
    'blog',
    'cla',
    'contact',
    'docs',
    'legacy',
    'releases',
    'svntogit',
    'tracdb',
    'fundraising.apps.FundraisingConfig',
]

LANGUAGE_CODE = 'en-us'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {"format": "[%(name)s] %(levelname)s: %(message)s"},
        "full": {"format": "%(asctime)s [%(name)s] %(levelname)s: %(message)s"},
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ['require_debug_false'],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
    }
}

MEDIA_ROOT = BASE.ancestor(2).child('media')

MEDIA_URL = '/m/'

MIDDLEWARE_CLASSES = [
    'djangosecure.middleware.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
]

ROOT_URLCONF = 'djangoproject.urls.www'

SECRET_KEY = str(SECRETS['secret_key'])

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

SERVER_EMAIL = "root@djangoproject.com"

SESSION_COOKIE_HTTPONLY = True

SILENCED_SYSTEM_CHECKS = ['1_6.W001']

SITE_ID = 1

STATICFILES_DIRS = [BASE.child('static')]

STATIC_ROOT = BASE.ancestor(2).child('static')

STATIC_URL = '/s/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'docs.context_processors.docs_version',
    'releases.context_processors.django_version',
    'aggregator.context_processors.community_stats',
    'django.core.context_processors.request',
]

TEMPLATE_DIRS = [BASE.child('templates')]

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = False

USE_TZ = False

# django-secure settings

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

# Haystack settings

HAYSTACK_SITECONF = 'docs.search_sites'

# django-contact-form / Akismet settings

AKISMET_API_KEY = "c892e4962244"

# django-hosts settings

DEFAULT_HOST = 'www'

HOST_OVERRIDE_URL_TAG = True

HOST_SCHEME = 'http'

HOST_SITE_TIMEOUT = 3600

ROOT_HOSTCONF = 'djangoproject.hosts'

# django-registration settings

ACCOUNT_ACTIVATION_DAYS = 3

# aggregator / PubSubHubbub settings

FEED_APPROVERS_GROUP_NAME = "feed-approver"

# django-push settings

PUSH_HUB = 'https://superfeedr.com/hubbub'

PUSH_CREDENTIALS = 'aggregator.utils.push_credentials'

# SUPERFEEDR_CREDS is a 2 element list in the form of [email,secretkey]
SUPERFEEDR_CREDS = SECRETS.get('superfeedr_creds')

# Stripe settings

# only testing keys as fallback values here please!
STRIPE_SECRET_KEY = SECRETS.get('STRIPE_SECRET_KEY',
                                'sk_test_x6zP4wd7Z5jcvDOJbbHZlHHt')
STRIPE_PUBLISHABLE_KEY = SECRETS.get('STRIPE_PUBLISHABLE_KEY',
                                     'pk_test_TyB5jcROwK8mlCNrn3dCwW7l')
