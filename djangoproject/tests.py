from http import HTTPStatus

from django.test import TestCase
from django_hosts.resolvers import reverse

from docs.models import DocumentRelease, Release


class TemplateViewTests(TestCase):
    """
    Tests for views that are instances of TemplateView.
    """

    def assertView(self, name):
        self.assertContains(self.client.get(reverse(name, host='www')), 'django')

    def test_homepage(self):
        self.assertView('homepage')

    def test_overview(self):
        self.assertView('overview')

    def test_start(self):
        self.assertView('start')

    def test_code_of_conduct(self):
        self.assertView('code_of_conduct')

    def test_conduct_faq(self):
        self.assertView('conduct_faq')

    def test_conduct_reporting(self):
        self.assertView('conduct_reporting')

    def test_conduct_enforcement(self):
        self.assertView('conduct_enforcement')

    def test_conduct_changes(self):
        self.assertView('conduct_changes')

    def test_styleguide(self):
        self.assertView('styleguide')


class ExcludeHostsLocaleMiddlewareTests(TestCase):
    """
    djangoproject.middleware.ExcludeHostsLocaleMiddleware properly prevents
    the hosts in settings.LOCALE_MIDDLEWARE_EXCLUDED_HOSTS from being
    processed by django.middleware.locale.LocaleMiddleware, as evidenced by
    the presence or absence of 'Content-Language' and 'Vary' headers in the
    response.
    """

    docs_host = 'docs.djangoproject.localhost'
    www_host = 'www.djangoproject.localhost'

    @classmethod
    def setUpTestData(cls):
        r2 = Release.objects.create(version='2.0')
        DocumentRelease.objects.create(lang='en', release=r2, is_default=True)

    def test_docs_host_excluded(self):
        "We get no Content-Language or Vary headers when docs host is excluded"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host]):
            resp = self.client.get('/', HTTP_HOST=self.docs_host)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertNotIn('Content-Language', resp)
        self.assertNotIn('Vary', resp)

    def test_docs_host_with_port_excluded(self):
        "We get no Content-Language or Vary headers when docs host (with a port) is excluded"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host]):
            resp = self.client.get('/', HTTP_HOST='%s:8000' % self.docs_host)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertNotIn('Content-Language', resp)
        self.assertNotIn('Vary', resp)

    def test_docs_host_forwarded_excluded(self):
        "We get no Content-Language or Vary headers when docs host (via X-Forwarded_host) is excluded"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host], USE_X_FORWARDED_HOST=True):
            resp = self.client.get('/', HTTP_X_FORWARDED_HOST=self.docs_host)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertNotIn('Content-Language', resp)
        self.assertNotIn('Vary', resp)

    def test_docs_host_not_excluded(self):
        "We still get Content-Language when docs host is not excluded"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[]):
            resp = self.client.get('/', HTTP_HOST=self.docs_host)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertIn('Content-Language', resp)
        self.assertIn('Vary', resp)

    def test_www_host(self):
        "www should still use LocaleMiddleware"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host]):
            resp = self.client.get('/', HTTP_HOST=self.www_host)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('Content-Language', resp)
        self.assertIn('Vary', resp)

    def test_www_host_with_port(self):
        "www (with a port) should still use LocaleMiddleware"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host]):
            resp = self.client.get('/', HTTP_HOST='%s:8000' % self.www_host)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('Content-Language', resp)
        self.assertIn('Vary', resp)
