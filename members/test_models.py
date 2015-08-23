from datetime import date

from django.test import TestCase
from django.views.generic.dates import timezone_today

from members.models import CorporateMember, DeveloperMember


class DeveloperMemberTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        DeveloperMember.objects.create(
            name='DjangoDeveloper',
            email='developer@example.com'
        )

    def setUp(self):
        self.member = DeveloperMember.objects.get(pk=1)

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
        CorporateMember.objects.create(
            display_name='Corporation',
            formal_name='Corporation',
            billing_email='c@example.com',
            contact_email='c@example.com',
            membership_level=2,
            membership_start=date(2011, 11, 11),
            membership_expires=date(2111, 11, 11),
            is_approved=True,
            address='Earth',
        )

    def setUp(self):
        self.member = CorporateMember.objects.get(pk=1)

    def test_str(self):
        self.assertEqual(str(self.member), 'Corporation')

    def test_initial_contact_should_have_default(self):
        self.assertEqual(CorporateMember().initial_contact_date, timezone_today())
