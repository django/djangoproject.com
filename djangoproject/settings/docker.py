from .dev import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": os.environ["SQL_ENGINE"],
        "NAME": os.environ["SQL_DATABASE"],
        "USER": os.environ["SQL_USER"],
        "PASSWORD": os.environ["SQL_PASSWORD"],
        "HOST": os.environ["SQL_HOST"],
        "PORT": os.environ["SQL_PORT"],
    },
    "trac": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["TRAC_DATABASE"],
        # "code.djangoproject" value is hardcoded in trac.sql
        "USER": "code.djangoproject",
        "PASSWORD": os.environ["TRAC_PASSWORD"],
        "HOST": os.environ["TRAC_HOST"],
        "PORT": os.environ["TRAC_PORT"],
    },
}


SECRET_KEY = os.environ.get("SECRET_KEY")

ALLOWED_HOSTS = [".localhost", "127.0.0.1", "www.127.0.0.1"]
