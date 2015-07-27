from django.core.urlresolvers import reverse
from django.test import TestCase


class DeveloperMemberListViewTests(TestCase):
    fixtures = ['members_test_data.json']

    def test_view_status_code(self):
        self.assertEqual(
            self.client.get(reverse('members:developer_members')).status_code,
            200
        )

    def test_view_render(self):
        response = self.client.get(reverse('members:developer_members'))
        self.assertContains(response, 'Developer Members')
        self.assertContains(response, 'DjangoDeveloper')

    def test_view_should_only_render_former_members_once(self):
        response = self.client.get(reverse('members:developer_members'))
        self.assertContains(response, 'FormerDjangoDeveloper', count=1)
