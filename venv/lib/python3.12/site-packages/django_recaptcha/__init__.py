import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SETTINGS_TYPES = {
    "RECAPTCHA_DOMAIN": str,
    "RECAPTCHA_PRIVATE_KEY": str,
    "RECAPTCHA_PROXY": dict,
    "RECAPTCHA_PUBLIC_KEY": str,
    "RECAPTCHA_VERIFY_REQUEST_TIMEOUT": int,
}

# Validate settings types.
for variable, instance_type in SETTINGS_TYPES.items():
    if hasattr(settings, variable) and not isinstance(
        getattr(settings, variable), instance_type
    ):
        raise ImproperlyConfigured(
            "Setting %s is not of type" % variable, instance_type
        )

if django.VERSION < (3, 2):
    default_app_config = "django_recaptcha.apps.DjangoRecaptchaConfig"
