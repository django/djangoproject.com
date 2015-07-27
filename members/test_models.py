from datetime import date, timedelta

from django.test import TestCase

from members.models import CorporateMember, DeveloperMember


class DeveloperMemberTests(TestCase):
    fixtures = ['members_test_data.json']

    def setUp(self):
        self.member = DeveloperMember.objects.get(pk=1)

    def test___str__(self):
        self.assertEqual(str(self.member), 'DjangoDeveloper')

    def test_member_since_should_have_default(self):
        self.assertEqual(DeveloperMember().member_since, date.today())

    def test_is_active(self):
        self.assertTrue(self.member.is_active)
        self.member.member_until = date.today()
        self.assertFalse(self.member.is_active)


class CorporateMemberTests(TestCase):
    fixtures = ['members_test_data.json']

    def setUp(self):
        self.member = CorporateMember.objects.get(pk=1)

    def test___str__(self):
        self.assertEqual(str(self.member), 'DSF')

    def test_initial_contact_should_have_default(self):
        self.assertEqual(CorporateMember().initial_contact_date, date.today())
