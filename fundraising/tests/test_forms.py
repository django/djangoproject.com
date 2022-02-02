from django.test import TestCase

from ..forms import PaymentForm


class TestPaymentForm(TestCase):
    def test_basics(self):
        form = PaymentForm(data={
            'amount': 100,
            'interval': 'onetime',
            'captcha': 'TESTING',
        })
        self.assertTrue(form.is_valid())

    def test_max_value_validation(self):
        """
        Reject unrealistic values greater than $1,000,000.
        """
        form = PaymentForm(data={
            'amount': 1_000_001,
            'interval': 'onetime',
            'captcha': 'TESTING',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_captcha_token_required(self):
        form = PaymentForm(data={
            'amount': 1_000,
            'interval': 'onetime',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('captcha', form.errors)
