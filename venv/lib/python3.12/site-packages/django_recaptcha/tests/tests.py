from importlib import reload

from django.core.checks import Error
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

import django_recaptcha


class TestInit(TestCase):
    def test_setting_instance_check(self):
        with override_settings(RECAPTCHA_PROXY="not a dict"):
            with self.assertRaises(ImproperlyConfigured) as error:
                reload(django_recaptcha)
            self.assertEqual(
                error.exception.args, ("Setting RECAPTCHA_PROXY is not of type", dict)
            )
        with override_settings(RECAPTCHA_VERIFY_REQUEST_TIMEOUT="not an int"):
            with self.assertRaises(ImproperlyConfigured) as error:
                reload(django_recaptcha)
            self.assertEqual(
                error.exception.args,
                ("Setting RECAPTCHA_VERIFY_REQUEST_TIMEOUT is not of type", int),
            )
        with override_settings(RECAPTCHA_DOMAIN=1):
            with self.assertRaises(ImproperlyConfigured) as error:
                reload(django_recaptcha)
            self.assertEqual(
                error.exception.args, ("Setting RECAPTCHA_DOMAIN is not of type", str)
            )
        with override_settings(RECAPTCHA_PUBLIC_KEY=1):
            with self.assertRaises(ImproperlyConfigured) as error:
                reload(django_recaptcha)
            self.assertEqual(
                error.exception.args,
                ("Setting RECAPTCHA_PUBLIC_KEY is not of type", str),
            )
        with override_settings(RECAPTCHA_PRIVATE_KEY=1):
            with self.assertRaises(ImproperlyConfigured) as error:
                reload(django_recaptcha)
            self.assertEqual(
                error.exception.args,
                ("Setting RECAPTCHA_PRIVATE_KEY is not of type", str),
            )

    @override_settings(
        RECAPTCHA_PRIVATE_KEY=django_recaptcha.constants.TEST_PRIVATE_KEY
    )
    def test_test_key_check(self):
        check_errors = django_recaptcha.checks.recaptcha_key_check("someconf")
        expected_errors = [
            Error(
                "RECAPTCHA_PRIVATE_KEY or RECAPTCHA_PUBLIC_KEY is making use"
                " of the Google test keys and will not behave as expected in a"
                " production environment",
                hint="Update settings.RECAPTCHA_PRIVATE_KEY"
                " and/or settings.RECAPTCHA_PUBLIC_KEY. Alternatively this"
                " check can be ignored by adding"
                " `SILENCED_SYSTEM_CHECKS ="
                " ['django_recaptcha.recaptcha_test_key_error']`"
                " to your settings file.",
                id="django_recaptcha.recaptcha_test_key_error",
            )
        ]
        self.assertEqual(check_errors, expected_errors)
