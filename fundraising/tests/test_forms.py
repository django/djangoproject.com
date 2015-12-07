from unittest.mock import patch

from django.test import TestCase

from ..forms import PaymentForm
from ..models import DjangoHero


class TestPaymentForm(TestCase):
    @patch('stripe.Customer.create')
    @patch('stripe.Charge.create')
    def test_make_donation(self, charge_create, customer_create):
        customer_create.return_value.id = 'xxxx'
        charge_create.return_value.id = 'xxxx'
        form = PaymentForm(data={
            'amount': 100,
            'stripe_token': 'xxxx',
            'interval': 'onetime',
            'receipt_email': 'django@example.com',
        })
        self.assertTrue(form.is_valid())
        donation = form.make_donation()
        self.assertEqual(100, donation.payment_set.first().amount)

    @patch('stripe.Customer.retrieve')
    @patch('stripe.Charge.create')
    def test_make_donation_with_existing_hero(self, charge_create, customer_retrieve):
        charge_create.return_value.id = 'XYZ'
        customer_retrieve.return_value.id = '12345'
        hero = DjangoHero.objects.create(
            email='django@example.com',
            stripe_customer_id=customer_retrieve.return_value.id,
        )
        form = PaymentForm(data={
            'amount': 100,
            'stripe_token': 'xxxx',
            'interval': 'onetime',
            'receipt_email': 'django@example.com',
        })
        self.assertTrue(form.is_valid())
        donation = form.make_donation()
        self.assertEqual(100, donation.payment_set.first().amount)
        self.assertEqual(hero, donation.donor)
        self.assertEqual(hero.stripe_customer_id, donation.stripe_customer_id)

    @patch('stripe.Customer.create')
    @patch('stripe.Charge.create')
    def test_make_donation_exception(self, charge_create, customer_create):
        customer_create.side_effect = ValueError("Something is wrong")
        form = PaymentForm(data={
            'amount': 100,
            'stripe_token': 'xxxx',
            'interval': 'onetime',
            'receipt_email': 'django@example.com',
        })
        self.assertTrue(form.is_valid())
        with self.assertRaises(ValueError):
            donation = form.make_donation()
            self.assertIsNone(donation)
