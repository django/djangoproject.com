import json
import shutil
import tempfile
from base64 import b64decode
from datetime import date, datetime
from operator import attrgetter
from unittest.mock import patch

import stripe
from django.conf import settings
from django.core import mail
from django.core.files.base import ContentFile
from django.template.defaultfilters import date as date_filter
from django.test import TestCase
from django.urls import reverse
from django_hosts.resolvers import reverse as django_hosts_reverse
from django_recaptcha.client import RecaptchaResponse

from members.models import CorporateMember, Invoice

from ..models import DjangoHero, Donation


class TemporaryMediaRootMixin:
    """
    A TestCase mixin that overrides settings.MEDIA_ROOT for every test on the
    class to point to a temporary directory that is destroyed when the tests
    finished.
    The content of the directory persists between different tests on the class.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmpdir = tempfile.mkdtemp(prefix="djangoprojectcom_")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)
        super().tearDownClass()

    def run(self, result=None):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            return super().run(result)


class TestIndex(TestCase):
    def test_redirect(self):
        response = self.client.get(reverse("fundraising:index"))
        self.assertEqual(response.status_code, 200)


class TestCampaign(TemporaryMediaRootMixin, TestCase):
    def setUp(self):
        self.index_url = reverse("fundraising:index")
        self.imagefile = ContentFile(
            content=b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAA"
                "DUlEQVR42mPk8Tb+DwACgAGLzMGnPAAAAABJRU5ErkJggg=="
            ),
            name="logo.png",
        )

    def test_corporate_member_without_logo(self):
        member = CorporateMember.objects.create(
            display_name="Test Member", membership_level=1, logo=None
        )
        Invoice.objects.create(amount=100, expiration_date=date.today(), member=member)
        response = self.client.get(self.index_url)

        self.assertContains(
            response,
            '<img src="/s/img/fundraising-heart.svg" alt="Pixelated heart logo">',
            html=True,
        )

    def test_corporate_member_with_logo(self):
        member = CorporateMember.objects.create(
            display_name="Test Member", membership_level=1, logo=self.imagefile
        )
        Invoice.objects.create(amount=100, expiration_date=date.today(), member=member)
        response = self.client.get(self.index_url)

        self.assertContains(
            response,
            """<img
                src="/m/cache/9b/e7/9be7b86ebc112b001cad84f900bf0bf7.png"
                srcset="/m/cache/9b/e7/9be7b86ebc112b001cad84f900bf0bf7@2x.png 2x"
                width="170"
                height="170"
                loading="lazy"
                alt="Logo of company Test Member"
            >""",
            html=True,
        )

    def test_anonymous_donor(self):
        hero = DjangoHero.objects.create(
            is_visible=True, approved=True, hero_type="individual"
        )
        donation = hero.donation_set.create(subscription_amount="5")
        donation.payment_set.create(amount="5")
        response = self.client.get(self.index_url)
        self.assertContains(response, "Anonymous Hero")

    def test_anonymous_donor_with_logo(self):
        hero = DjangoHero.objects.create(
            is_visible=True,
            approved=True,
            hero_type="individual",
            logo=self.imagefile,
        )
        donation = hero.donation_set.create(subscription_amount="5")
        donation.payment_set.create(amount="5")
        response = self.client.get(self.index_url)
        self.assertContains(response, "Anonymous Hero")

    def test_submitting_donation_form_invalid_amount(self):
        url = reverse("fundraising:donation-session")
        response = self.client.post(
            url,
            {
                "amount": "superbad",
                "interval": "onetime",
            },
        )
        content = json.loads(response.content.decode())
        self.assertEqual(200, response.status_code)
        self.assertFalse(content["success"])

    @patch("stripe.checkout.Session.create")
    @patch("django_recaptcha.fields.client.submit")
    def test_submitting_donation_form_valid(self, client_submit, session_create):
        session_create.return_value = {"id": "TEST_ID"}
        client_submit.return_value = RecaptchaResponse(is_valid=True, action="form")
        response = self.client.post(
            reverse("fundraising:donation-session"),
            {
                "amount": 100,
                "interval": "onetime",
                "captcha": "TESTING",
            },
        )
        content = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(content["success"])
        self.assertEqual(content["sessionId"], "TEST_ID")

    @patch("stripe.Customer.retrieve")
    def test_cancel_donation(self, retrieve_customer):
        donor = DjangoHero.objects.create()
        donation = Donation.objects.create(
            donor=donor,
            stripe_subscription_id="12345",
            stripe_customer_id="54321",
        )
        url = reverse("fundraising:cancel-donation", kwargs={"hero": donor.id})
        response = self.client.post(url, {"donation": donation.id})
        self.assertRedirects(
            response, reverse("fundraising:manage-donations", kwargs={"hero": donor.id})
        )
        retrieve_customer.assert_called_once_with("54321")
        donation = Donation.objects.get(id=donation.id)
        self.assertEqual("", donation.stripe_subscription_id)

    @patch("stripe.Customer.retrieve")
    def test_cancel_already_cancelled_donation(self, retrieve_customer):
        donor = DjangoHero.objects.create()
        donation = Donation.objects.create(donor=donor, stripe_subscription_id="")
        url = reverse("fundraising:cancel-donation", kwargs={"hero": donor.id})
        response = self.client.post(url, {"donation": donation.id})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(retrieve_customer.called)


class TestThankYou(TestCase):
    def setUp(self):
        self.url = reverse("fundraising:thank-you")

    def test_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "fundraising/thank-you.html")


class TestManageDonations(TestCase):
    past_donations_header = "<h2>Your past donations</h2>"

    @classmethod
    def setUpTestData(cls):
        cls.hero = DjangoHero.objects.create()
        cls.donation1 = cls.hero.donation_set.create(
            interval="onetime",
            subscription_amount=5,
        )
        cls.payment1 = cls.donation1.payment_set.create(
            amount="5",
            stripe_charge_id="c1",
            date=datetime(2023, 1, 1),
        )
        cls.donation2 = cls.hero.donation_set.create(
            interval="yearly",
            subscription_amount=10,
        )
        cls.payment2 = cls.donation2.payment_set.create(
            amount="10",
            stripe_charge_id="c2",
            date=datetime(2024, 1, 1),
        )
        cls.url = reverse("fundraising:manage-donations", kwargs={"hero": cls.hero.id})

    @staticmethod
    def _format_donation_date(value):
        return date_filter(value, "DATETIME_FORMAT")

    def test_past_donations(self):
        response = self.client.get(self.url)
        self.assertCountEqual(
            response.context["past_payments"], [self.payment1, self.payment2]
        )
        self.assertContains(response, self.past_donations_header)
        self.assertContains(
            response,
            "<li>$10.00 on %s (Yearly donation)</li>"
            % self._format_donation_date(self.payment1.date),
            html=True,
        )
        self.assertContains(
            response,
            "$5.00 on %s (One-time donation)"
            % self._format_donation_date(self.payment2.date),
            html=True,
        )

    def test_no_past_donations(self):
        hero = DjangoHero.objects.create()
        url = reverse("fundraising:manage-donations", kwargs={"hero": hero.id})
        response = self.client.get(url)
        self.assertNotContains(response, self.past_donations_header)

    def test_past_donations_sorted(self):
        url = reverse("fundraising:manage-donations", kwargs={"hero": self.hero.id})
        response = self.client.get(url)
        self.assertQuerySetEqual(
            response.context["past_payments"],
            ["c2", "c1"],
            transform=attrgetter("stripe_charge_id"),
        )


class TestWebhooks(TestCase):
    def setUp(self):
        self.hero = DjangoHero.objects.create(email="hero@djangoproject.com")
        self.donation = Donation.objects.create(
            donor=self.hero,
            interval="monthly",
            stripe_customer_id="cus_3MXPY5pvYMWTBf",
            stripe_subscription_id="sub_3MXPaZGXvVZSrS",
        )

    def stripe_data(self, filename):
        file_path = settings.BASE_DIR.joinpath(f"fundraising/test_data/{filename}.json")
        with file_path.open() as f:
            data = json.load(f)
            return stripe.util.convert_to_stripe_object(data, stripe.api_key, None)

    def post_event(self):
        return self.client.post(
            reverse("fundraising:receive-webhook"),
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
        self.assertTrue(response.status_code, 422)

    @patch("stripe.Event.retrieve")
    def test_empty_object(self, event):
        event.return_value = self.stripe_data("empty_payment")
        response = self.post_event()
        self.assertEqual(response.status_code, 422)

    @patch("stripe.Event.retrieve")
    def test_zero_invoice_amount(self, event):
        """Zero payment amounts don't need to be created."""
        event.return_value = self.stripe_data("zero_invoice_amount")
        response = self.post_event()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.donation.payment_set.count(), 0)
