import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'push.sqlite'),
    },
}

INSTALLED_APPS = (
    'django.contrib.sites',
    'django_push.subscriber',
    'tests.publisher',
    'tests.subscribe',
)

STATIC_URL = '/static/'

SECRET_KEY = 'test secret key'

ROOT_URLCONF = 'tests.publisher.urls'

SITE_ID = 1

PUSH_DOMAIN = 'testserver.com'

MIDDLEWARE = ()
