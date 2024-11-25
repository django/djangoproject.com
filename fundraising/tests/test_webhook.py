import json
from unittest.mock import patch

import stripe
from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django_hosts.resolvers import reverse as django_hosts_reverse

from ..models import DjangoHero, Donation, Payment
from stripe import util as stripe_util

class TestWebhooks(TestCase):
    def setUp(self):
        self.hero = DjangoHero.objects.create(email="hero@djangoproject.com")
        self.donation = Donation.objects.create(
            donor=self.hero,
            interval="monthly",
            stripe_customer_id="cus_3MXPY5pvYMWTBf",
            stripe_subscription_id="sub_3MXPaZGXvVZSrS",
        )
        self.url = reverse('fundraising:receive-webhook')

    def stripe_data(self, filename):
        file_path = settings.BASE_DIR.joinpath(f"fundraising/test_data/{filename}.json")
        with file_path.open() as f:
            data = json.load(f)
            return stripe.util.convert_to_stripe_object(data, stripe.api_key, None)

    def post_event(self):
        return self.client.post(
            self.url,
            data='{"id": "evt_12345"}',
            content_type="application/json",
        )

    @patch("stripe.Event.retrieve")
    def test_record_payment(self, event):
        event.return_value = self.stripe_data("invoice_succeeded")
        response = self.post_event()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.donation.payment_set.count(), 1)
        payment = self.donation.payment_set.first()
        self.assertEqual(payment.amount, 10)

    @patch("stripe.Event.retrieve")
    def test_subscription_cancelled(self, event):
        event.return_value = self.stripe_data("subscription_cancelled")
        self.post_event()
        donation = Donation.objects.get(id=self.donation.id)
        self.assertEqual(donation.stripe_subscription_id, "")
        self.assertEqual(len(mail.outbox), 1)
        expected_url = django_hosts_reverse("fundraising:index")
        self.assertTrue(expected_url in mail.outbox[0].body)

    @patch("stripe.Event.retrieve")
    def test_payment_failed(self, event):
        event.return_value = self.stripe_data("payment_failed")
        self.post_event()
        self.assertEqual(len(mail.outbox), 1)
        expected_url = django_hosts_reverse(
            "fundraising:manage-donations", kwargs={"hero": self.hero.id}
        )
        self.assertTrue(expected_url in mail.outbox[0].body)

    @patch("stripe.Event.retrieve")
    def test_no_such_event(self, event):
        event.side_effect = stripe.error.InvalidRequestError(
            message="No such event: evt_12345", param="id"
        )
        response = self.post_event()
        self.assertEqual(response.status_code, 422)

    @patch("stripe.Event.retrieve")
    def test_empty_object(self, event):
        event.return_value = self.stripe_data("empty_payment")
        response = self.post_event()
        self.assertEqual(response.status_code, 422)

    @patch('stripe.Event.retrieve')
    @patch('stripe.Customer.retrieve')
    @patch('stripe.PaymentIntent.retrieve')
    def test_checkout_session_completed_atomic(self, mock_payment_intent, mock_customer, mock_event):
        session_data = {
            'id': 'cs_test_123',
            'customer': 'cus_123',
            'amount_total': 5000,  # $50.00
            'payment_intent': 'pi_123',
            'mode': 'payment',
            'subscription': None
        }

        # Create proper Stripe event structure
        event_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": stripe_util.convert_to_stripe_object(
                    session_data,
                    stripe.api_key,
                    None
                )
            }
        }
        mock_event.return_value = stripe_util.convert_to_stripe_object(
            event_data,
            stripe.api_key,
            None
        )

        mock_customer.return_value = stripe_util.convert_to_stripe_object(
            {
                'id': 'cus_123',
                'email': 'donor@example.com',
            },
            stripe.api_key,
            None
        )

        mock_payment_intent.return_value.charges.data = [
            stripe_util.convert_to_stripe_object(
                {'id': 'ch_123'},
                stripe.api_key,
                None
            )
        ]

        # Mock Donation.objects.create to raise an exception
        with patch('fundraising.models.Donation.objects.create') as mock_create:
            mock_create.side_effect = Exception('Database error')

            response = self.client.post(
                self.url,
                data='{"id":"evt_123"}',
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 500)
            self.assertEqual(DjangoHero.objects.count(), 1)  # Only the one from setUp
            self.assertEqual(Donation.objects.count(), 1)    # Only the one from setUp
            self.assertEqual(Payment.objects.count(), 0)
