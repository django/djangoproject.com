from datetime import date, timedelta

from django.test import TestCase
from members.models import CorporateMember, DeveloperMember


class DeveloperMemberTests(TestCase):

    def setUp(self):
        self.member = DeveloperMember.objects.create(
            name='Developer',
            email='member@example.com',
        )

    def test___str__(self):
        self.assertEqual(str(self.member), 'Developer')

    def test_member_since_should_have_default(self):
        self.assertEqual(DeveloperMember().member_since, date.today())

    def test_is_active(self):
        self.assertTrue(self.member.is_active)
        self.member.member_until = date.today()
        self.assertFalse(self.member.is_active)


class CorporateMemberTests(TestCase):

    def setUp(self):
        self.member = CorporateMember.objects.create(
            display_name='DSF',
            formal_name='Django Software Foundation',
            contact_email='dsf@example.com',
            billing_email='dsf@example.com',
            url='https://djangoproject.com',
            description='...',
            membership_level=1,
            membership_start=date.today(),
            membership_expires=date.today() + timedelta(days=365),
            address='Earth'

        )

    def test___str__(self):
        self.assertEqual(str(self.member), 'DSF')

    def test_initial_contact_should_have_default(self):
        self.assertEqual(CorporateMember().initial_contact_date, date.today())
