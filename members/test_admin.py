from datetime import date, timedelta

from django.contrib import admin
from django.test import TestCase

from .admin import CorporateMemberAdmin, StatusFilter
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
        cls.inactive_member = CorporateMember.objects.create(
            display_name='Inactive Corporation',
            billing_name='inactive',
            billing_email='d@example.com',
            contact_email='d@example.com',
            membership_level=2,
            inactive=True,
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
        expected_str = '<a href="http://www.djangoproject.localhost:8000/foundation/corporate-membership/renew/'
        modeladmin = CorporateMemberAdmin(CorporateMember, admin.site)
        self.assertTrue(modeladmin.renewal_link(self.member).startswith(expected_str))

    def test_status_filter(self):
        members = CorporateMember.objects.all()
        filter_args = {'request': None, 'params': {}, 'model': None, 'model_admin': None}
        self.assertCountEqual(
            StatusFilter(**filter_args).queryset(request=None, queryset=members),
            [self.member]
        )
        filter_args['params'] = {'status': 'inactive'}
        self.assertCountEqual(
            StatusFilter(**filter_args).queryset(None, CorporateMember.objects.all()),
            [self.inactive_member]
        )
        filter_args['params'] = {'status': 'all'}
        self.assertCountEqual(
            StatusFilter(**filter_args).queryset(None, CorporateMember.objects.all()),
            [self.member, self.inactive_member]
        )
        status_filter = StatusFilter(**filter_args)
        self.assertEqual(
            status_filter.lookups(request=None, model_admin=None),
            (
                (None, 'Active'),
                ('inactive', 'Inactive'),
                ('all', 'All'),
            )
        )

        class MockChangeList:
            def get_query_string(self, *args):
                return ''
        self.assertEqual(
            list(status_filter.choices(cl=MockChangeList())),
            [
                {'display': 'Active', 'query_string': '', 'selected': True},
                {'display': 'Inactive', 'query_string': '', 'selected': False},
                {'display': 'All', 'query_string': '', 'selected': False},
            ]
        )
