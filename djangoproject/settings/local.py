# djangoproject/settings/local.py
from .dev import *  # Import all dev settings


ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'djangoproject',
        'USER': 'djangoproject',
        'PASSWORD': 'Nath76a1',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}