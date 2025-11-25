from django.conf import settings
from django.core import checks

from django_recaptcha.constants import TEST_PRIVATE_KEY, TEST_PUBLIC_KEY


def recaptcha_key_check(app_configs, **kwargs):
    errors = []
    private_key = getattr(settings, "RECAPTCHA_PRIVATE_KEY", TEST_PRIVATE_KEY)
    public_key = getattr(settings, "RECAPTCHA_PUBLIC_KEY", TEST_PUBLIC_KEY)

    if private_key == TEST_PRIVATE_KEY or public_key == TEST_PUBLIC_KEY:
        errors.extend(
            [
                checks.Error(
                    "RECAPTCHA_PRIVATE_KEY or RECAPTCHA_PUBLIC_KEY is making use"
                    " of the Google test keys and will not behave as expected in a"
                    " production environment",
                    hint="Update settings.RECAPTCHA_PRIVATE_KEY"
                    " and/or settings.RECAPTCHA_PUBLIC_KEY. Alternatively this check"
                    " can be ignored by adding"
                    " `SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']`"
                    " to your settings file.",
                    id="django_recaptcha.recaptcha_test_key_error",
                )
            ]
        )
    return errors
