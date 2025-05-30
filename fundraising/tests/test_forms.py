from unittest.mock import patch

from django.test import TestCase
from django_recaptcha.client import RecaptchaResponse

from ..forms import DonationForm, PaymentForm
from ..models import DjangoHero, Donation


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

    @patch("fundraising.forms.stripe.Subscription.retrieve", side_effect=KeyError)
    def test_donation_form_save_atomic(self, *mocks):
        """
        A stripe error in save() should rollback any change made to the Donation
        """
        donation = Donation.objects.create(
            interval="monthly",
            subscription_amount=50,
            donor=DjangoHero.objects.create(),
        )
        form = DonationForm(
            instance=donation,
            data={"subscription_amount": 25, "interval": "yearly"},
        )

        # Save the form, this will trigger a KeyError but we catch it and move on
        self.assertTrue(form.is_valid())
        self.assertRaises(KeyError, form.save)

        # The donation should not have been updated with new data
        donation.refresh_from_db()
        self.assertEqual(donation.interval, "monthly")
        self.assertEqual(donation.subscription_amount, 50)
