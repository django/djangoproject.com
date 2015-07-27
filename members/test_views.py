from datetime import date

from django.core.urlresolvers import reverse
from django.test import TestCase

from members.models import CorporateMember, DeveloperMember


class DeveloperMemberListViewTests(TestCase):
    url = reverse('members:developer_members')

    @classmethod
    def setUpTestData(cls):
        DeveloperMember.objects.create(
            name='DjangoDeveloper',
            email='developer@example.com'
        )

    def test_view_status_code(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_view_render(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Developer members')
        self.assertContains(response, 'DjangoDeveloper')

    def test_view_should_only_render_former_members_once(self):
        DeveloperMember.objects.create(
            name='FormerDjangoDeveloper',
            email='developer@example.com',
            member_since=date(2015, 7, 26),
            member_until=date(2015, 7, 27)
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'FormerDjangoDeveloper', count=1)


class CorporateMemberListViewTests(TestCase):
    url = reverse('members:corporate_members')

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

    def test_view_status_code(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_view_render(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Corporate members')
        self.assertContains(response, 'Corporation')

    def test_view_should_not_render_unapproved(self):
        CorporateMember.objects.create(
            display_name='Corporation unapproved',
            formal_name='Corporation',
            billing_email='c@example.com',
            contact_email='c@example.com',
            membership_level=2,
            membership_start=date(2011, 11, 11),
            membership_expires=date(2111, 11, 11),
            is_approved=False,
            address='Earth',
        )
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Corporation unapproved')

    def test_view_should_only_render_former_members_once(self):
        CorporateMember.objects.create(
            display_name='Corporation expired',
            formal_name='Corporation',
            billing_email='c@example.com',
            contact_email='c@example.com',
            membership_level=2,
            membership_start=date(2011, 11, 11),
            membership_expires=date(2012, 11, 11),
            is_approved=True,
            address='Earth',
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Corporation expired', count=1)
