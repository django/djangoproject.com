from django.apps import AppConfig
from django.core.checks import Tags, register

from django_recaptcha.checks import recaptcha_key_check


class DjangoRecaptchaConfig(AppConfig):
    name = "django_recaptcha"
    verbose_name = "Django reCAPTCHA"

    def ready(self):
        register(recaptcha_key_check, Tags.security)
