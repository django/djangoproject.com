from datetime import date, timedelta

from django.test import TestCase

from members.models import (
    GOLD_MEMBERSHIP, PLATINUM_MEMBERSHIP, SILVER_MEMBERSHIP, CorporateMember,
    IndividualMember, Team,
)


class IndividualMemberTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = IndividualMember.objects.create(
            name='DjangoDeveloper',
            email='developer@example.com'
        )

    def setUp(self):
        self.member.refresh_from_db()

    def test_str(self):
        self.assertEqual(str(self.member), 'DjangoDeveloper')

    def test_member_since_should_have_default(self):
        self.assertEqual(IndividualMember().member_since, date.today())

    def test_is_active(self):
        self.assertTrue(self.member.is_active)
        self.member.member_until = date.today()
        self.assertFalse(self.member.is_active)


class CorporateMemberTests(TestCase):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    @classmethod
    def setUpTestData(cls):
        cls.member = CorporateMember.objects.create(
            display_name='Corporation',
            billing_name='foo',
            billing_email='c@example.com',
            contact_email='c@example.com',
            membership_level=SILVER_MEMBERSHIP,
        )

    def setUp(self):
        self.member.refresh_from_db()

    def test_str(self):
        self.assertEqual(str(self.member), 'Corporation')

    def test_is_invoiced(self):
        # No invoices == not invoiced.
        self.assertEqual(self.member.is_invoiced, False)
        # Invoice but no sent_date == not invoiced.
        invoice = self.member.invoice_set.create(amount=500)
        self.assertEqual(self.member.is_invoiced, False)
        # Invoice with an sent_date == invoiced.
        invoice.sent_date = self.today
        invoice.save()
        self.assertEqual(self.member.is_invoiced, True)

    def test_is_paid(self):
        # No invoices == not paid.
        self.assertEqual(self.member.is_paid, False)
        # Invoice but no paid_date == not paid.
        invoice = self.member.invoice_set.create(amount=500)
        self.assertEqual(self.member.is_paid, False)
        # Invoice with a paid_date == paid.
        invoice.paid_date = self.today
        invoice.save()
        self.assertEqual(self.member.is_paid, True)

    def test_get_expiry_date(self):
        self.assertIsNone(self.member.get_expiry_date())
        self.member.invoice_set.create(amount=500)
        self.assertIsNone(self.member.get_expiry_date())
        self.member.invoice_set.create(amount=500, expiration_date=self.today)
        self.assertEqual(self.member.get_expiry_date(), self.today)
        self.member.invoice_set.create(amount=500, expiration_date=self.tomorrow)
        self.assertEqual(self.member.get_expiry_date(), self.tomorrow)

    def test_manager_by_membership_level(self):
        self.assertEqual(CorporateMember.objects.by_membership_level(), {})
        self.member.invoice_set.create(amount=500, expiration_date=self.tomorrow)
        self.assertEqual(CorporateMember.objects.by_membership_level(), {'silver': [self.member]})
        self.member.membership_level = GOLD_MEMBERSHIP
        self.member.save()
        self.assertEqual(CorporateMember.objects.by_membership_level(), {'gold': [self.member]})
        self.member.membership_level = PLATINUM_MEMBERSHIP
        self.member.save()
        self.assertEqual(CorporateMember.objects.by_membership_level(), {'platinum': [self.member]})


class TeamTests(TestCase):

    def test_str(self):
        self.assertEqual(str(Team(name='Ops')), 'Ops')
