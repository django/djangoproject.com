from unittest.mock import patch

from django.test import TestCase

from djangoproject.tests import patch_captcha

from ..forms import DjangoHeroForm, DonationForm, PaymentForm
from ..models import DISPLAY_DONOR_DAYS, LEADERSHIP_LEVEL_AMOUNT, DjangoHero, Donation


class TestPaymentForm(TestCase):
    def test_basics(self):
        form = PaymentForm(
            data={
                "amount": 100,
                "interval": "onetime",
                "captcha": "TESTING",
            }
        )
        with patch_captcha():
            self.assertTrue(form.is_valid(), form.errors)

    def test_max_value_validation(self):
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
        with patch_captcha():
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


class TestDjangoHeroForm(TestCase):
    def test_logo_help_text_states_the_display_window(self):
        """The logo help text matches DjangoHeroManager.for_public_display().

        Only donations from the last DISPLAY_DONOR_DAYS days count towards the
        leadership level, so the help text has to say so (refs #1766).
        """
        help_text = DjangoHeroForm().fields["logo"].help_text
        self.assertIn(f"US ${LEADERSHIP_LEVEL_AMOUNT:.0f}", help_text)
        self.assertIn(f"in the last {DISPLAY_DONOR_DAYS} days", help_text)
