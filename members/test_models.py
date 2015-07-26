from datetime import date

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
