from django.contrib.admin import helpers
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from fundraising.models import DjangoHero


class CustomViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super_user = User.objects.create_superuser(username="superuser")

    def setUp(self):
        super().setUp()
        self.client.force_login(self.super_user)

    def test_download_donor_report(self):
        a_hero = DjangoHero.objects.create(approved=True, is_visible=True)
        donation = a_hero.donation_set.create(interval="onetime")
        donation.payment_set.create(
            amount=42,
            stripe_charge_id=get_random_string(length=12),
        )
        response = self.client.post(
            reverse("admin:fundraising_djangohero_changelist"),
            {
                "action": "download_donor_report",
                helpers.ACTION_CHECKBOX_NAME: [a_hero.pk],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            "\r\n".join(
                [
                    "name,email,alternate email,last gift date,gift amount (US$),"
                    "interval,recurring active?,location",
                    f",,,{timezone.now():%Y-%m-%d},42.00,One-time ,,",
                    "",  # empty end line
                ]
            ).encode(),
        )

    def test_download_donor_report_get_latest_payment(self):
        a_hero = DjangoHero.objects.create(approved=True, is_visible=True)
        donation = a_hero.donation_set.create(interval="onetime")
        donation.payment_set.create(
            amount=42,
            stripe_charge_id=get_random_string(length=12),
        )
        donation.payment_set.create(
            amount=21,
            stripe_charge_id=get_random_string(length=12),
        )
        response = self.client.post(
            reverse("admin:fundraising_djangohero_changelist"),
            {
                "action": "download_donor_report",
                helpers.ACTION_CHECKBOX_NAME: [a_hero.pk],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            "\r\n".join(
                [
                    "name,email,alternate email,last gift date,gift amount (US$),"
                    "interval,recurring active?,location",
                    f",,,{timezone.now():%Y-%m-%d},21.00,One-time,,",
                    "",  # empty end line
                ]
            ).encode(),
        )
