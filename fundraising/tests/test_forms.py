from unittest.mock import patch

from django.test import TestCase
from django_recaptcha.client import RecaptchaResponse

from ..forms import PaymentForm


class TestPaymentForm(TestCase):
    @patch("django_recaptcha.fields.client.submit")
    def test_basics(self, client_submit):
        client_submit.return_value = RecaptchaResponse(is_valid=True, action="form")
        form = PaymentForm(
            data={
                "amount": 100,
                "interval": "onetime",
                "captcha": "TESTING",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    @patch("django_recaptcha.fields.client.submit")
    def test_max_value_validation(self, client_submit):
        client_submit.return_value = RecaptchaResponse(is_valid=True, action="form")
        """
        Reject unrealistic values greater than $1,000,000.
        """
        form = PaymentForm(
            data={
                "amount": 1_000_000,
                "interval": "onetime",
                "captcha": "TESTING",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_captcha_token_required(self):
        form = PaymentForm(
            data={
                "amount": 1_000,
                "interval": "onetime",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("captcha", form.errors)
