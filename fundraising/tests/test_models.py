from datetime import date

from django.test import TestCase

from ..models import DjangoHero, Donation, InKindDonor
from .utils import ImageFileFactory, TemporaryMediaRootMixin


class TestDjangoHero(TemporaryMediaRootMixin, TestCase):
    def setUp(self):
        kwargs = {
            "approved": True,
            "is_visible": True,
        }
        self.h1 = DjangoHero.objects.create(**kwargs)
        d1 = self.h1.donation_set.create()
        d1.payment_set.create(amount="5", stripe_charge_id="a1")
        self.h2 = DjangoHero.objects.create(**kwargs)
        d2 = self.h2.donation_set.create()
        d2.payment_set.create(amount="15", stripe_charge_id="a2")
        self.h3 = DjangoHero.objects.create(**kwargs)
        d3 = self.h3.donation_set.create()
        d3.payment_set.create(amount="10", stripe_charge_id="a3")
        self.today = date.today()

    def test_thumbnail(self):
        self.h1.logo = ImageFileFactory(name="logo.jpeg")
        self.h1.save()
        thumbnail = self.h1.thumbnail
        self.assertEqual(thumbnail.x, 170)
        self.assertEqual(thumbnail.y, 170)
        self.h1.logo.delete()
        self.assertTrue(thumbnail.exists())

    def test_thumbnail_no_logo(self):
        self.assertIsNone(self.h2.thumbnail)

    def test_name_with_fallback(self):
        hero = DjangoHero()
        self.assertEqual(hero.name_with_fallback, "Anonymous Hero")
        hero.name = "Batistek"
        self.assertEqual(hero.name_with_fallback, "Batistek")

    def test_display_name(self):
        hero = DjangoHero(name="Hero")
        self.assertEqual(hero.display_name, "Hero")


class TestDonation(TestCase):
    def test_is_active(self):
        self.assertFalse(Donation().is_active())
        self.assertTrue(Donation(stripe_subscription_id="abc").is_active())


class TestInKindDonor(TestCase):
    def test_display_name(self):
        donor = InKindDonor(name="Hero")
        self.assertEqual(donor.display_name, "Hero")
