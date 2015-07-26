from datetime import date, timedelta

from django.core.urlresolvers import reverse
from django.test import TestCase

from members.models import CorporateMember, DeveloperMember


# Inherit from TestCase to enable these tests.
class DeveloperMemberListViewTests(object):
    # url = reverse('members:developer-members')

    @classmethod
    def setUpTestData(cls):
        DeveloperMember.objects.create(
            name='DjangoDeveloper',
            email='developer@example.com'
        )

    def test_view_render(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Developer members')
        self.assertContains(response, 'DjangoDeveloper')

    def test_view_should_only_render_former_members_once(self):
        DeveloperMember.objects.create(
            name='FormerDjangoDeveloper',
            email='developer@example.com',
            member_since=date(2015, 7, 26),
            member_until=date(2015, 7, 27),
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'FormerDjangoDeveloper', count=1)


class CorporateMemberListViewTests(TestCase):
    url = reverse('members:corporate-members')

    @classmethod
    def setUpTestData(cls):
        cls.today = today = date.today()
        member = CorporateMember.objects.create(
            display_name='Corporation',
            contact_email='c@example.com',
            membership_level=2,
        )
        member.invoice_set.create(
            sent_date=today,
            amount=500,
            paid_date=today,
            expiration_date=today + timedelta(days=1),
        )

    def test_view_render(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Corporate members')
        self.assertContains(response, 'Corporation')

    def test_view_should_not_render_unapproved(self):
        CorporateMember.objects.create(
            display_name='Corporation unapproved',
            contact_email='c@example.com',
            membership_level=2,
        )
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Corporation unapproved')
