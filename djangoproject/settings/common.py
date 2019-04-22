# Settings for www.djangoproject.com
import json
import os
from pathlib import Path

# Utilities
PROJECT_PACKAGE = Path(__file__).resolve().parent.parent

# The full path to the repository root.
BASE_DIR = PROJECT_PACKAGE.parent

data_dir_key = 'DJANGOPROJECT_DATA_DIR'
DATA_DIR = Path(os.environ[data_dir_key]) if data_dir_key in os.environ else BASE_DIR.parent

try:
    with DATA_DIR.joinpath('conf', 'secrets.json').open() as handle:
        SECRETS = json.load(handle)
except IOError:
    SECRETS = {
        'secret_key': 'a',
        'superfeedr_creds': ['any@email.com', 'some_string'],
    }


# Django settings

CACHE_MIDDLEWARE_SECONDS = 60 * 5  # 5 minutes

CACHE_MIDDLEWARE_KEY_PREFIX = 'django'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangoproject',
        'USER': 'djangoproject',
        'HOST': SECRETS.get('db_host', ''),
        'PASSWORD': SECRETS.get('db_password', ''),
        'PORT': SECRETS.get('db_port', ''),
    },
    'trac': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'code.djangoproject',
        'USER': 'code.djangoproject',
        'HOST': SECRETS.get('trac_db_host', ''),
        'PASSWORD': SECRETS.get('trac_db_password', ''),
        'PORT': SECRETS.get('trac_db_port', ''),
    }
}

DATABASE_ROUTERS = ['tracdb.db_router.TracRouter']

DEFAULT_FROM_EMAIL = "noreply@djangoproject.com"
FUNDRAISING_DEFAULT_FROM_EMAIL = "fundraising@djangoproject.com"

FIXTURE_DIRS = [str(PROJECT_PACKAGE.joinpath('fixtures'))]

INSTALLED_APPS = [
    'accounts',
    'aggregator',
    'blog',
    'contact',
    'dashboard',
    'docs.apps.DocsConfig',
    'foundation',
    'legacy',
    'members',
    'releases',
    'svntogit',
    'tracdb',
    'fundraising',

    'registration',
    'django_hosts',
    'sorl.thumbnail',
    'djmoney',

    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_push.subscriber',
]

LANGUAGE_CODE = 'en-us'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {"format": "[%(name)s] %(levelname)s: %(message)s"},
        "full": {"format": "%(asctime)s [%(name)s] %(levelname)s: %(message)s"},
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    "loggers": {
        "django.request": {
            "handlers": [],
            "level": "ERROR",
            "propagate": False,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

LOGIN_REDIRECT_URL = 'edit_profile'

MEDIA_URL = '/m/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_hosts.middleware.HostsRequestMiddleware',
    # Put LocaleMiddleware before SessionMiddleware to prevent the former from accessing the
    # session and adding 'Vary: Cookie' to all responses.
    'djangoproject.middleware.ExcludeHostsLocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'accounts.hashers.PBKDF2WrappedSHA1PasswordHasher',
]

ROOT_URLCONF = 'djangoproject.urls.www'

SECRET_KEY = str(SECRETS['secret_key'])

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

SERVER_EMAIL = "root@djangoproject.com"

SESSION_COOKIE_HTTPONLY = True

SILENCED_SYSTEM_CHECKS = [
    'fields.W342',  # tracdb has ForeignKey(unique=True) in lieu of multi-col PKs
    'security.W008',  # SSL redirect is handled by nginx
    'security.W009',  # SECRET_KEY is setup through Ansible secrets
]

SITE_ID = 1

STATICFILES_DIRS = [str(PROJECT_PACKAGE.joinpath('static'))]

STATIC_URL = '/s/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(PROJECT_PACKAGE.joinpath('templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins': [
                'django_hosts.templatetags.hosts_override',
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'docs.context_processors.docs_version',
                'releases.context_processors.django_version',
                'aggregator.context_processors.community_stats',
                'django.template.context_processors.request',
            ],
        },
    },
]

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = False

USE_TZ = False

# django-contact-form / Akismet settings

AKISMET_API_KEY = "c892e4962244"

# django-hosts settings

DEFAULT_HOST = 'www'

HOST_SCHEME = 'http'

HOST_SITE_TIMEOUT = 3600

ROOT_HOSTCONF = 'djangoproject.hosts'

# django-registration settings

ACCOUNT_ACTIVATION_DAYS = 3

REGISTRATION_EMAIL_HTML = False

# aggregator / PubSubHubbub settings

FEED_APPROVERS_GROUP_NAME = "feed-approver"

# django-push settings

PUSH_HUB = 'https://push.superfeedr.com/'

PUSH_CREDENTIALS = 'aggregator.utils.push_credentials'

# SUPERFEEDR_CREDS is a 2 element list in the form of [email,secretkey]
SUPERFEEDR_CREDS = SECRETS.get('superfeedr_creds')

# Fastly credentials
FASTLY_API_KEY = SECRETS.get('fastly_api_key')
FASTLY_SERVICE_URL = SECRETS.get('fastly_service_url')

# Stripe settings

# only testing keys as fallback values here please!
STRIPE_SECRET_KEY = SECRETS.get('stripe_secret_key', 'sk_test_x6zP4wd7Z5jcvDOJbbHZlHHt')
STRIPE_PUBLISHABLE_KEY = SECRETS.get('stripe_publishable_key', 'pk_test_TyB5jcROwK8mlCNrn3dCwW7l')

# sorl-thumbnail settings
THUMBNAIL_PRESERVE_FORMAT = True
THUMBNAIL_ALTERNATIVE_RESOLUTIONS = [2]

# dashboard settings
TRAC_RPC_URL = "https://code.djangoproject.com/rpc"
TRAC_URL = "https://code.djangoproject.com/"
