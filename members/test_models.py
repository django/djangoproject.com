from datetime import date, timedelta

from django.test import TestCase

from members.models import CorporateMember, DeveloperMember


class DeveloperMemberTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = DeveloperMember.objects.create(
            name='DjangoDeveloper',
            email='developer@example.com'
        )

    def setUp(self):
        self.member.refresh_from_db()

    def test_str(self):
        self.assertEqual(str(self.member), 'DjangoDeveloper')

    def test_member_since_should_have_default(self):
        self.assertEqual(DeveloperMember().member_since, date.today())

    def test_is_active(self):
        self.assertTrue(self.member.is_active)
        self.member.member_until = date.today()
        self.assertFalse(self.member.is_active)


class CorporateMemberTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = CorporateMember.objects.create(
            display_name='Corporation',
            billing_name='foo',
            billing_email='c@example.com',
            contact_email='c@example.com',
            membership_level=2,
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
        invoice.sent_date = date.today()
        invoice.save()
        self.assertEqual(self.member.is_invoiced, True)

    def test_is_paid(self):
        # No invoices == not paid.
        self.assertEqual(self.member.is_paid, False)
        # Invoice but no paid_date == not paid.
        invoice = self.member.invoice_set.create(amount=500)
        self.assertEqual(self.member.is_paid, False)
        # Invoice with a paid_date == paid.
        invoice.paid_date = date.today()
        invoice.save()
        self.assertEqual(self.member.is_paid, True)

    def test_get_expiry_date(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        self.assertIsNone(self.member.get_expiry_date())
        self.member.invoice_set.create(amount=500)
        self.assertIsNone(self.member.get_expiry_date())
        self.member.invoice_set.create(amount=500, expiration_date=today)
        self.assertEqual(self.member.get_expiry_date(), today)
        self.member.invoice_set.create(amount=500, expiration_date=tomorrow)
        self.assertEqual(self.member.get_expiry_date(), tomorrow)
