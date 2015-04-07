from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django_hosts.resolvers import reverse


class ViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='a-user')

    @mock.patch('accounts.views.get_user_stats')
    def test_user_profile(self, mock_user_stats):
        response = self.client.get(reverse('user_profile', host='www', args=['a-user']))
        self.assertContains(response, 'a-user')
        mock_user_stats.assert_called_once_with(self.user)
