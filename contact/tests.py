from unittest import skipIf

import requests
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings


def check_network_connection():
    try:
        requests.get('https://djangoproject.com')
    except requests.exceptions.ConnectionError:
        return False
    return True


has_network_connection = check_network_connection()


@override_settings(AKISMET_TESTING=True)
class ContactFormTests(TestCase):
    def setUp(self):
        self.url = '/contact/foundation/'

    @override_settings(AKISMET_API_KEY='')  # Disable Akismet in tests
    def test_invalid_email(self):
        response = self.client.post(self.url, {
            'name': 'A. Random Hacker',
            'email': 'xxx',
            'message_subject': 'Hello',
            'body': 'Hello, World!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', ['Enter a valid email address.'])

    @override_settings(AKISMET_API_KEY='')  # Disable Akismet in tests
    def test_without_akismet(self):
        response = self.client.post(self.url, {
            'name': 'A. Random Hacker',
            'email': 'a.random@example.com',
            'message_subject': 'Hello',
            'body': 'Hello, World!'
        })
        self.assertRedirects(response, '/contact/sent/')
        self.assertEqual(mail.outbox[-1].subject, '[Contact form] Hello')

    @skipIf(not has_network_connection, 'Requires a network connection')
    def test_empty_name(self):
        response = self.client.post(self.url, {
            'name': '',
            'email': 'a.random@example.com',
            'message_subject': 'Hello',
            'body': 'Hello, World!',
        })
        self.assertFormError(response, 'form', 'name', ['This field is required.'])

    @skipIf(not has_network_connection, 'Requires a network connection')
    def test_akismet_detect_spam(self):
        response = self.client.post(self.url, {
            'name': 'viagra-test-123',  # according to akismet this should flag as spam
            'email': 'a.random@example.com',
            'message_subject': 'Hello',
            'body': 'Hello, World!'
        })
        self.assertContains(response, 'Akismet thinks this message is spam')
        self.assertEqual(len(mail.outbox), 0)

    @skipIf(not has_network_connection, 'Requires a network connection')
    def test_akismet_not_spam(self):
        response = self.client.post(self.url, {
            'name': 'administrator',
            'email': 'a.random@example.com',
            'message_subject': 'Hello',
            'body': 'Hello, World!'
        })
        self.assertRedirects(response, '/contact/sent/')
        self.assertEqual(mail.outbox[-1].subject, '[Contact form] Hello')
