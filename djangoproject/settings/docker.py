from .dev import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE"),
        "NAME": os.environ.get("SQL_DATABASE"),
        "USER": os.environ.get("SQL_USER"),
        "PASSWORD": os.environ.get("SQL_PASSWORD"),
        "HOST": os.environ.get("SQL_HOST"),
        "PORT": os.environ.get("SQL_PORT"),
    }
}

# Trac connection
DATABASES["trac"] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ.get("TRAC_DATABASE", "code.djangoproject"),
    "USER": os.environ.get("TRAC_USER", "code.djangoproject"),
    "PASSWORD": os.environ.get("TRAC_PASSWORD", ""),
    "HOST": os.environ.get("TRAC_HOST", "db"),
    "PORT": os.environ.get("TRAC_PORT", "5432"),
}

SECRET_KEY = os.environ.get("SECRET_KEY")

ALLOWED_HOSTS = [".localhost", "127.0.0.1", "www.127.0.0.1"]

LOCALE_MIDDLEWARE_EXCLUDED_HOSTS = ["docs.djangoproject.localhost"]

# django-hosts settings
PARENT_HOST = "djangoproject.localhost:8000"
