try:
    from unittest import mock
except ImportError:
    import mock

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TransactionTestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone

from django_push.subscriber.models import Subscription, SubscriptionError
from django_push.subscriber.utils import get_domain
from django_push.subscriber.signals import updated

from .. import response


class SubscriberTestCase(TransactionTestCase):
    def setUp(self):
        self.signals = []
        updated.connect(self._signal_handler)

    def _signal_handler(self, sender, notification, **kwargs):
        self.signals.append([sender, notification, kwargs])

    @override_settings(INSTALLED_APPS=[])
    @mock.patch('requests.post')
    def test_subscribing(self, post):
        post.return_value = response(status_code=202)
        s = Subscription.objects.subscribe("http://example.com/feed",
                                           "http://hub.domain.com/hub")
        url = reverse('subscriber_callback', args=[s.pk])
        post.assert_called_once_with(
            'http://hub.domain.com/hub',
            data={
                'hub.callback': 'http://testserver.com{0}'.format(url),
                'hub.verify': ['sync', 'async'],
                'hub.topic': 'http://example.com/feed',
                'hub.mode': 'subscribe',
            },
            auth=None,
            timeout=None,
        )

        s = Subscription.objects.get(pk=s.pk)
        self.assertIs(s.verified, False)
        self.assertIs(s.lease_expiration, None)

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_subscribe_no_hub_warning(self, post, get):
        post.return_value = response(status_code=202)
        get.return_value = response(status_code=200, content="""<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en-us"><title></title><link href="http://testserver/overriden-feed/" rel="alternate"></link><link href="http://testserver/override-feed/" rel="self"></link><id>http://testserver/overriden-feed/</id><updated>2013-06-23T10:58:30Z</updated><link href="http://example.com/overridden-hub" rel="hub"></link></feed>""")  # noqa

    @mock.patch('requests.post')
    def test_subscription_secret(self, post):
        post.return_value = response(status_code=202)
        s = Subscription.objects.subscribe(
            'http://foo.com/insecure', hub='http://insecure.example.com/hub')
        self.assertEqual(s.secret, '')
        s = Subscription.objects.subscribe(
            'http://foo.com/secure', hub='https://secure.example.com/hub')
        self.assertEqual(len(s.secret), 50)

    @mock.patch('requests.post')
    def test_sync_subscribing(self, post):
        post.return_value = response(status_code=204)
        Subscription.objects.subscribe("http://example.com/feed",
                                       "http://hub.domain.com/hub")
        self.assertEqual(len(post.call_args_list), 1)
        subscription = Subscription.objects.get()
        self.assertEqual(subscription.verified, True)

    def test_get_domain(self):
        self.assertEqual(get_domain(), 'testserver.com')
        push_domain = settings.PUSH_DOMAIN
        del settings.PUSH_DOMAIN
        self.assertEqual(get_domain(), 'example.com')

        with self.settings(INSTALLED_APPS=[]):
            with self.assertRaises(ImproperlyConfigured):
                get_domain()

        settings.PUSH_DOMAIN = push_domain

    @mock.patch('requests.post')
    def test_manager_unsubscribe(self, post):
        post.return_value = response(status_code=202)
        s = Subscription.objects.create(topic='http://example.com/feed',
                                        hub='http://hub.example.com')
        post.assert_not_called()
        s.unsubscribe()
        post.assert_called_once_with(
            'http://hub.example.com',
            data={
                'hub.callback': s.callback_url,
                'hub.verify': ['sync', 'async'],
                'hub.topic': 'http://example.com/feed',
                'hub.mode': 'unsubscribe',
            },
            auth=None,
            timeout=None,
        )

    @mock.patch('requests.post')
    def test_subscribe_lease_seconds(self, post):
        post.return_value = response(status_code=202)
        with self.settings(PUSH_LEASE_SECONDS=14):  # overriden in the call
            s = Subscription.objects.subscribe('http://test.example.com/feed',
                                               hub='http://hub.example.com',
                                               lease_seconds=12)
        post.assert_called_once_with(
            'http://hub.example.com',
            data={
                'hub.callback': s.callback_url,
                'hub.verify': ['sync', 'async'],
                'hub.topic': 'http://test.example.com/feed',
                'hub.mode': 'subscribe',
                'hub.lease_seconds': 12,
            },
            auth=None,
            timeout=None,
        )

    @mock.patch('requests.post')
    def test_subscribe_timeout(self, post):
        post.return_value = response(status_code=202)
        with self.settings(PUSH_TIMEOUT=10):  # overriden in the call
            s = Subscription.objects.subscribe('http://test.example.com/feed',
                                               hub='http://hub.example.com',
                                               )
        post.assert_called_once_with(
            'http://hub.example.com',
            data={
                'hub.callback': s.callback_url,
                'hub.verify': ['sync', 'async'],
                'hub.topic': 'http://test.example.com/feed',
                'hub.mode': 'subscribe',
            },
            auth=None,
            timeout=10,
        )

    @mock.patch('requests.post')
    def test_lease_seconds_from_settings(self, post):
        post.return_value = response(status_code=202)
        with self.settings(PUSH_LEASE_SECONDS=2592000):
            s = Subscription.objects.subscribe('http://test.example.com/feed',
                                               hub='http://hub.example.com')
        post.assert_called_once_with(
            'http://hub.example.com',
            data={
                'hub.callback': s.callback_url,
                'hub.verify': ['sync', 'async'],
                'hub.topic': 'http://test.example.com/feed',
                'hub.mode': 'subscribe',
                'hub.lease_seconds': 2592000,
            },
            auth=None,
            timeout=None,
        )

    @mock.patch('requests.post')
    def test_subscription_error(self, post):
        post.return_value = response(status_code=200)
        with self.assertRaises(SubscriptionError):
            Subscription.objects.subscribe('http://example.com/test',
                                           hub='http://hub.example.com')

    @override_settings(PUSH_CREDENTIALS='tests.subscribe.credentials')
    @mock.patch('requests.post')
    def test_hub_credentials(self, post):
        post.return_value = response(status_code=202)
        s = Subscription.objects.subscribe('http://example.com/test',
                                           hub='http://hub.example.com')
        post.assert_called_once_with(
            'http://hub.example.com',
            data={
                'hub.callback': s.callback_url,
                'hub.verify': ['sync', 'async'],
                'hub.topic': 'http://example.com/test',
                'hub.mode': 'subscribe',
            },
            auth=('username', 'password'),
            timeout=None,
        )

    def test_missing_callback_params(self):
        s = Subscription.objects.create(topic='foo', hub='bar')
        url = reverse('subscriber_callback', args=[s.pk])
        response = self.client.get(url)
        self.assertContains(
            response,
            "Missing parameters: hub.mode, hub.topic, hub.challenge",
            status_code=400,
        )

    def test_wrong_topic(self):
        s = Subscription.objects.create(topic='foo', hub='bar')
        url = reverse('subscriber_callback', args=[s.pk])
        response = self.client.get(url, {
            'hub.topic': 'baz',
            'hub.mode': 'subscribe',
            'hub.challenge': 'challenge yo',
        })
        self.assertContains(response, 'Mismatching topic URL', status_code=400)

    def test_wrong_mode(self):
        s = Subscription.objects.create(topic='foo', hub='bar')
        url = reverse('subscriber_callback', args=[s.pk])
        response = self.client.get(url, {
            'hub.topic': 'foo',
            'hub.mode': 'modemode',
            'hub.challenge': 'challenge yo',
        })
        self.assertContains(response, 'Unrecognized hub.mode parameter',
                            status_code=400)

    def test_missing_lease_seconds(self):
        s = Subscription.objects.create(topic='foo', hub='bar')
        url = reverse('subscriber_callback', args=[s.pk])
        response = self.client.get(url, {
            'hub.topic': 'foo',
            'hub.mode': 'subscribe',
            'hub.challenge': 'challenge yo',
        })
        self.assertContains(response, 'Missing hub.lease_seconds parameter',
                            status_code=400)

    def test_improper_lease_seconds(self):
        s = Subscription.objects.create(topic='foo', hub='bar')
        url = reverse('subscriber_callback', args=[s.pk])
        response = self.client.get(url, {
            'hub.topic': 'foo',
            'hub.mode': 'subscribe',
            'hub.challenge': 'challenge yo',
            'hub.lease_seconds': 'yo',
        })
        self.assertContains(response, 'hub.lease_seconds must be an integer',
                            status_code=400)

    def test_verify_subscription(self):
        s = Subscription.objects.create(topic='foo', hub='bar')
        self.assertFalse(s.verified)
        self.assertIs(s.lease_expiration, None)
        self.assertFalse(s.has_expired())

        url = reverse('subscriber_callback', args=[s.pk])
        response = self.client.get(url, {
            'hub.topic': 'foo',
            'hub.mode': 'subscribe',
            'hub.challenge': 'challenge yo',
            'hub.lease_seconds': 12345,
        })
        self.assertContains(response, 'challenge yo')

        s = Subscription.objects.get(pk=s.pk)
        self.assertTrue(s.verified)
        self.assertTrue(
            12345 - (s.lease_expiration - timezone.now()).seconds < 3
        )
        self.assertFalse(s.has_expired())

    def test_verify_unsubscription(self):
        s = Subscription.objects.create(topic='foo', hub='bar')

        url = reverse('subscriber_callback', args=[s.pk])
        response = self.client.get(url, {
            'hub.topic': 'foo',
            'hub.mode': 'unsubscribe',
            'hub.challenge': 'challenge yo',
        })
        self.assertEqual(response.content.decode(), 'challenge yo')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Subscription.objects.count(), 0)

    def test_payload_no_secret(self):
        s = Subscription.objects.create(topic='foo', hub='bar')
        url = reverse('subscriber_callback', args=[s.pk])

        self.assertEqual(len(self.signals), 0)
        response = self.client.post(url, 'foo', content_type='text/plain')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.signals), 1)
        sender, notification = self.signals[0][:2]
        self.assertEqual(sender, s)
        self.assertEqual(notification, b'foo')

    def test_payload_missing_secret(self):
        s = Subscription.objects.create(topic='foo', hub='bar', secret='lol')
        url = reverse('subscriber_callback', args=[s.pk])

        response = self.client.post(url, 'foo', content_type='text/plain')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.signals), 0)

    def test_payload_wrong_signature(self):
        s = Subscription.objects.create(topic='foo', hub='bar', secret='lol')
        url = reverse('subscriber_callback', args=[s.pk])

        response = self.client.post(url, 'foo', content_type='text/plain',
                                    HTTP_X_HUB_SIGNATURE='sha1=deadbeef')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.signals), 0)

    def test_payload_correct_signature(self):
        s = Subscription.objects.create(topic='foo', hub='bar', secret='lol')
        url = reverse('subscriber_callback', args=[s.pk])

        sig = 'sha1=bfe9c8b0bc631a74dbc484c4e4a5a469cbb8b01f'
        response = self.client.post(url, 'foo', content_type='text/plain',
                                    HTTP_X_HUB_SIGNATURE=sig)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.signals), 1)

    def test_payload_link_headers(self):
        s = Subscription.objects.create(topic='foo', hub='bar')
        url = reverse('subscriber_callback', args=[s.pk])

        self.assertEqual(len(self.signals), 0)
        response = self.client.post(
            url, 'foo', content_type='text/plain', HTTP_LINK=(
                '<http://joemygod.blogspot.com/feeds/posts/default>; '
                'rel="self",<http://pubsubhubbub.appspot.com/>; rel="hub"'
            ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.signals), 1)
        for link in self.signals[0][2]['links']:
            if link['rel'] == 'self':
                break
        self.assertEqual(link['url'],
                         "http://joemygod.blogspot.com/feeds/posts/default")
