from .common import INSTALLED_APPS

DEBUG = False
SECRET_KEY = 'test-secret-key'

INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "foundation"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
