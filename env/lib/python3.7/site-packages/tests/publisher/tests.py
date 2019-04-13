try:
    from unittest import mock
except ImportError:
    import mock

from django.urls import reverse
from django.test import TestCase
from django.test.utils import override_settings

from django_push import UA
from django_push.publisher import ping_hub


class PubTestCase(TestCase):
    @mock.patch('requests.post')
    def test_explicit_ping(self, post):
        post.return_value = 'Response'
        with self.assertRaises(ValueError):
            ping_hub('http://example.com/feed')

        ping_hub('http://example.com/feed', hub_url='http://example.com/hub')
        post.assert_called_once_with(
            'http://example.com/hub',
            headers={'User-Agent': UA},
            data={'hub.url': 'http://example.com/feed',
                  'hub.mode': 'publish'})

    @mock.patch('requests.post')
    @override_settings(PUSH_HUB='http://hub.example.com')
    def test_ping_settings(self, post):
        post.return_value = 'Response'
        ping_hub('http://example.com/feed')
        post.assert_called_once_with(
            'http://hub.example.com',
            headers={'User-Agent': UA},
            data={'hub.url': 'http://example.com/feed',
                  'hub.mode': 'publish'})

    @mock.patch('requests.post')
    @override_settings(PUSH_HUB='http://hub.example.com')
    def test_ping_settings_override(self, post):
        post.return_value = 'Response'
        ping_hub('http://example.com/feed', hub_url='http://google.com')
        post.assert_called_once_with(
            'http://google.com',
            headers={'User-Agent': UA},
            data={'hub.url': 'http://example.com/feed',
                  'hub.mode': 'publish'})

    @override_settings(PUSH_HUB='http://hub.example.com')
    def test_hub_declaration(self):
        response = self.client.get(reverse('feed'))
        hub_declaration = response.content.decode('utf-8').split(
            '</updated>', 1)[1].split('<entry>', 1)[0]
        self.assertEqual(len(hub_declaration), 53)
        self.assertTrue('rel="hub"' in hub_declaration)
        self.assertTrue('href="http://hub.example.com' in hub_declaration)

        response = self.client.get(reverse('override-feed'))
        hub_declaration = response.content.decode('utf-8').split(
            '</updated>', 1)[1].split('<entry>', 1)[0]
        self.assertEqual(len(hub_declaration), 64)
        self.assertTrue('rel="hub"' in hub_declaration)
        self.assertFalse('href="http://hub.example.com' in hub_declaration)
        self.assertTrue(
            'href="http://example.com/overridden-hub' in hub_declaration
        )

        response = self.client.get(reverse('dynamic-feed'))
        hub_declaration = response.content.decode('utf-8').split(
            '</updated>', 1)[1].split('<entry>', 1)[0]
        self.assertEqual(len(hub_declaration), 62)
        self.assertTrue('rel="hub"' in hub_declaration)
        self.assertFalse('href="http://hub.example.com' in hub_declaration)
        self.assertTrue(
            'href="http://dynamic-hub.example.com/' in hub_declaration
        )

    def test_no_hub(self):
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
