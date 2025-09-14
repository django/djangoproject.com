from datetime import date, datetime, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils.crypto import get_random_string

from members.models import CorporateMember

from ..models import (
    DISPLAY_DONOR_DAYS,
    GOAL_START_DATE,
    LEADERSHIP_LEVEL_AMOUNT,
    DjangoHero,
    InKindDonor,
    Payment,
)
from ..templatetags.fundraising_extras import (
    display_django_heroes,
    donation_form_with_heart,
    top_corporate_members,
)


class TestDonationFormWithHeart(TestCase):
    def test_donors_count(self):
        # Donor with a Payment after GOAL_START_DATE
        donor1 = DjangoHero.objects.create()
        donation1 = donor1.donation_set.create()
        donation1.payment_set.create(amount=1, stripe_charge_id="a")
        donation1.payment_set.create(amount=2, stripe_charge_id="b")
        # Donor with a Payment before GOAL_START_DATE
        past_donor = DjangoHero.objects.create()
        past_donation = past_donor.donation_set.create()
        past_payment = past_donation.payment_set.create(amount=4, stripe_charge_id="c")
        past_date = GOAL_START_DATE - timedelta(days=1)
        Payment.objects.filter(pk=past_payment.pk).update(date=past_date)
        member = CorporateMember.objects.create(membership_level=1)
        member.invoice_set.create(amount=5, paid_date=GOAL_START_DATE)
        # Invoice with paid_date before GOAL_START_DATE shouldn't appear.
        member.invoice_set.create(amount=25, paid_date=past_date)
        response = donation_form_with_heart({"user": None})
        self.assertEqual(response["total_donors"], 1)
        self.assertEqual(response["donated_amount"], Decimal("8.00"))


class TestDisplayDjangoHeroes(TestCase):
    def test_display_django_heroes(self):
        def create_hero_with_payment_amount(amount):
            hero = DjangoHero.objects.create(
                email="%s@djangoproject.com" % get_random_string(length=12),
                approved=True,
                is_visible=True,
            )
            donation = hero.donation_set.create(interval="onetime")
            donation.payment_set.create(
                amount=amount,
                stripe_charge_id=get_random_string(length=12),
            )
            return hero

        hero1 = create_hero_with_payment_amount(LEADERSHIP_LEVEL_AMOUNT + 1)
        hero2 = create_hero_with_payment_amount(LEADERSHIP_LEVEL_AMOUNT)
        hero3 = create_hero_with_payment_amount(LEADERSHIP_LEVEL_AMOUNT - 1)
        inkind_donor = InKindDonor.objects.create(name="Inkind")

        response = display_django_heroes()
        self.assertEqual(response["leaders"], [hero1, hero2])
        self.assertEqual(response["heroes"], [hero3])
        self.assertEqual(list(response["inkind_donors"]), [inkind_donor])

    def test_display_django_heroes_payments(self):
        """
        Donors created more than DISPLAY_DONOR_DAYS ago shouldn't be displayed.
        """

        def create_hero_with_payment_date(days):
            hero = DjangoHero.objects.create(
                email="%s@djangoproject.com" % get_random_string(length=12),
                approved=True,
                is_visible=True,
            )
            donation = hero.donation_set.create(interval="onetime")
            payment = donation.payment_set.create(
                amount=10 + days,
                stripe_charge_id=get_random_string(length=12),
            )
            date = datetime.today() - timedelta(days=DISPLAY_DONOR_DAYS + days)
            Payment.objects.filter(pk=payment.pk).update(date=date)
            return hero

        create_hero_with_payment_date(1)
        hero2 = create_hero_with_payment_date(0)
        hero3 = create_hero_with_payment_date(-1)

        response = display_django_heroes()
        self.assertEqual(response["heroes"], [hero2, hero3])


class TestTopCorporateMembers(TestCase):
    past_date = date(2000, 1, 1)
    future_date = date(3000, 1, 1)

    @classmethod
    def setUpTestData(cls):
        member_1 = CorporateMember.objects.create(membership_level=1)
        member_2 = CorporateMember.objects.create(membership_level=2)
        member_3 = CorporateMember.objects.create(membership_level=3)
        member_4 = CorporateMember.objects.create(membership_level=4)
        member_5 = CorporateMember.objects.create(membership_level=5)

        member_1.invoice_set.create(amount=5, expiration_date=cls.future_date)
        member_2.invoice_set.create(amount=5, expiration_date=cls.future_date)
        member_3.invoice_set.create(amount=5, expiration_date=cls.future_date)
        member_4.invoice_set.create(amount=5, expiration_date=cls.past_date)
        member_5.invoice_set.create(amount=5, expiration_date=cls.past_date)

    def test_with_no_platinum_or_diamond_members(self):
        members = top_corporate_members()["members"]

        self.assertEqual(members, [])

    def test_with_diamond_members_and_no_platinum_members(self):
        member_1 = CorporateMember.objects.create(membership_level=5)
        member_2 = CorporateMember.objects.create(membership_level=5)
        member_3 = CorporateMember.objects.create(membership_level=5)

        member_1.invoice_set.create(amount=4, expiration_date=self.future_date)
        member_2.invoice_set.create(amount=8, expiration_date=self.future_date)
        member_3.invoice_set.create(amount=2, expiration_date=self.future_date)

        members = top_corporate_members()["members"]

        self.assertEqual(members, [member_2, member_1, member_3])

    def test_with_platinum_members_and_no_diamond_members(self):
        member_1 = CorporateMember.objects.create(membership_level=4)
        member_2 = CorporateMember.objects.create(membership_level=4)
        member_3 = CorporateMember.objects.create(membership_level=4)

        member_1.invoice_set.create(amount=4, expiration_date=self.future_date)
        member_2.invoice_set.create(amount=8, expiration_date=self.future_date)
        member_3.invoice_set.create(amount=2, expiration_date=self.future_date)

        members = top_corporate_members()["members"]

        self.assertEqual(members, [member_2, member_1, member_3])

    def test_with_diamond_members_and_platinum_members(self):
        member_1 = CorporateMember.objects.create(membership_level=4)
        member_2 = CorporateMember.objects.create(membership_level=4)
        member_3 = CorporateMember.objects.create(membership_level=4)

        member_4 = CorporateMember.objects.create(membership_level=5)
        member_5 = CorporateMember.objects.create(membership_level=5)
        member_6 = CorporateMember.objects.create(membership_level=5)

        member_1.invoice_set.create(amount=4, expiration_date=self.future_date)
        member_2.invoice_set.create(amount=8, expiration_date=self.future_date)
        member_3.invoice_set.create(amount=2, expiration_date=self.future_date)

        member_4.invoice_set.create(amount=4, expiration_date=self.future_date)
        member_5.invoice_set.create(amount=8, expiration_date=self.future_date)
        member_6.invoice_set.create(amount=2, expiration_date=self.future_date)

        members = top_corporate_members()["members"]

        expected = [member_5, member_4, member_6, member_2, member_1, member_3]

        self.assertEqual(members, expected)
