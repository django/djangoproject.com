from datetime import date, timedelta

from django.contrib import admin
from django.test import TestCase

from .admin import CorporateMemberAdmin
from .models import CorporateMember


class CorporateMemberAdminTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = CorporateMember.objects.create(
            display_name='Corporation',
            billing_name='foo',
            billing_email='c@example.com',
            contact_email='c@example.com',
            membership_level=2,
        )

    def test_membership_expires(self):
        today = date.today()
        yesterday = date.today() - timedelta(days=1)
        plus_thirty_one_days = today + timedelta(days=31)
        modeladmin = CorporateMemberAdmin(CorporateMember, admin.site)
        self.assertIsNone(modeladmin.membership_expires(self.member))
        self.member.invoice_set.create(amount=500)
        self.assertIsNone(modeladmin.membership_expires(self.member))
        self.member.invoice_set.create(amount=500, expiration_date=yesterday)
        self.assertIn('red', modeladmin.membership_expires(self.member))
        self.member.invoice_set.create(amount=500, expiration_date=today)
        self.assertIn('orange', modeladmin.membership_expires(self.member))
        self.member.invoice_set.create(amount=500, expiration_date=plus_thirty_one_days)
        self.assertIn('green', modeladmin.membership_expires(self.member))

    def test_renewal_link(self):
        expected_str = '<a href="http://www.djangoproject.dev:8000/foundation/corporate-membership/renew/'
        modeladmin = CorporateMemberAdmin(CorporateMember, admin.site)
        self.assertTrue(modeladmin.renewal_link(self.member).startswith(expected_str))
