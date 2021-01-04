from django.test import TestCase

from ..forms import PaymentForm


class TestPaymentForm(TestCase):
    def test_basics(self):
        form = PaymentForm(data={
            'amount': 100,
            'interval': 'onetime',
        })
        self.assertTrue(form.is_valid())
