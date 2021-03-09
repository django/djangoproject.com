from django.test import TestCase

from ..forms import PaymentForm


class TestPaymentForm(TestCase):
    def test_basics(self):
        form = PaymentForm(data={
            'amount': 100,
            'interval': 'onetime',
        })
        self.assertTrue(form.is_valid())

    def test_max_value_validation(self):
        """
        Reject unrealistic values greater than $1,000,000.
        """
        form = PaymentForm(data={
            'amount': 1_000_001,
            'interval': 'onetime',
        })
        self.assertFalse(form.is_valid())
