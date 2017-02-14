from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from .models import CorporateMember, IndividualMember, Team
from .utils import get_temporary_image


class IndividualMemberListViewTests(TestCase):
    url = reverse('members:individual-members')

    @classmethod
    def setUpTestData(cls):
        IndividualMember.objects.create(
            name='DjangoDeveloper',
            email='developer@example.com'
        )

    def test_developer_member_redirect(self):
        old_url = reverse('members:developer-members')
        response = self.client.get(old_url)
        self.assertRedirects(response, self.url)

    def test_view_render(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Individual members')
        self.assertContains(response, 'DjangoDeveloper')

    def test_view_should_only_render_former_members_once(self):
        IndividualMember.objects.create(
            name='FormerDjangoDeveloper',
            email='developer2@example.com',
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
        cls.member = CorporateMember.objects.create(
            display_name='Corporation',
            contact_email='c@example.com',
            membership_level=2,
        )
        cls.member.invoice_set.create(
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

    def test_view_renders_orgs_by_tier(self):
        member = CorporateMember.objects.create(
            display_name='AAA',
            contact_email='c@example.com',
            membership_level=2,
        )
        member.invoice_set.create(
            sent_date=self.today,
            # shouldn't sort by amount
            amount=self.member.invoice_set.first().amount - 1,
            paid_date=self.today,
            expiration_date=self.today + timedelta(days=1),
        )
        response = self.client.get(self.url)
        members = response.context['members']
        self.assertEqual(
            sorted(members.keys()),
            ['bronze', 'diamond', 'gold', 'platinum', 'silver']
        )
        self.assertQuerysetEqual(
            members['silver'],
            ['<CorporateMember: Corporation>', '<CorporateMember: AAA>']
        )


class CorporateMemberJoinViewTests(TestCase):

    def test_get(self):
        response = self.client.get(reverse('members:corporate-members-join'))
        self.assertContains(response, "Become a DSF corporate member")

    def test_submit_success(self):
        data = {
            'display_name': 'Foo Widgets',
            'billing_name': 'Foo Widgets, Inc.',
            'logo': get_temporary_image(),
            'url': 'http://example.com',
            'contact_name': 'Joe Developer',
            'contact_email': 'joe@example.com',
            'billing_email': '',
            'membership_level': 2,
            'address': 'USA',
            'description': 'We make widgets!',
            'django_usage': 'fun',
            'amount': 2000,
        }
        response = self.client.post(reverse('members:corporate-members-join'), data)
        self.assertRedirects(response, reverse('members:corporate-members-join-thanks'))
        member = CorporateMember.objects.latest('id')
        self.assertEqual(member.display_name, data['display_name'])
        self.assertEqual(member.invoice_set.get().amount, data['amount'])


class CorporateMemberRenewalViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = CorporateMember.objects.create(
            display_name='Corporation',
            contact_email='c@example.com',
            membership_level=2,
        )

    def test_get(self):
        response = self.client.get(self.member.get_renewal_link())
        self.assertContains(response, 'Become a DSF corporate member')
        self.assertEqual(response.context['form'].instance, self.member)

    def test_invalid_token(self):
        url = reverse('members:corporate-members-renew', kwargs={'token': 'aaaaa'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TeamListViewTests(TestCase):
    url = reverse('members:teams')

    @classmethod
    def setUpTestData(cls):
        dev = IndividualMember.objects.create(
            name='DjangoDeveloper',
            email='developer@example.com',
        )
        cls.security_team = Team.objects.create(name='Security team')
        cls.ops_team = Team.objects.create(name='Ops team', slug='ops', description='Ops stuff.')
        cls.ops_team.members.add(dev)

    def test_get(self):
        response = self.client.get(self.url)
        # Sorted by name
        self.assertSequenceEqual(response.context['teams'], [self.ops_team, self.security_team])
        self.assertContains(response, '<h3 id="ops-team">Ops team</h3>')
        self.assertContains(response, '<p>Ops stuff.</p>')
        self.assertContains(response, '<ul><li>DjangoDeveloper</li></ul>', html=True)
