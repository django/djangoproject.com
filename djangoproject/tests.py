from http import HTTPStatus
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import NoReverseMatch, get_resolver
from django.utils.translation import activate, gettext as _
from django_hosts.resolvers import reverse

from docs.models import DocumentRelease, Release


class LocaleSmokeTests(TestCase):
    """
    Smoke test a translated string from each of the 3 locale directories
    (one defined in settings.LOCALE_PATHS, plus the dashboard and docs apps).
    """

    def test_dashboard_locale(self):
        """dashboard/locale/ should contain translations for 'Development dashboard'"""
        activate("fr")
        translated = _("Development dashboard")
        self.assertEqual(
            translated,
            "Tableau de bord de développement",
            msg="dashboard/locale/ translation not loaded or incorrect",
        )

    def test_docs_locale(self):
        """docs/locale/ should contain translations for 'Using Django'"""
        activate("fr")
        translated = _("Using Django")
        self.assertEqual(
            translated,
            "Utilisation de Django",
            msg="docs/locale/ translation not loaded or incorrect",
        )

    def test_project_locale(self):
        """locale/ should contain translations for 'Fundraising'"""
        activate("fr")
        translated = _("Fundraising")
        self.assertEqual(
            translated,
            "Levée de fonds",
            msg="project-level locale/ translation not loaded or incorrect",
        )


class TemplateViewTests(TestCase):
    """
    Tests for views that are instances of TemplateView.
    """

    def assertView(self, name):
        self.assertContains(self.client.get(reverse(name, host="www")), "django")

    def test_homepage(self):
        self.assertView("homepage")

    def test_overview(self):
        self.assertView("overview")

    def test_start(self):
        self.assertView("start")

    def test_code_of_conduct(self):
        self.assertView("code_of_conduct")

    def test_conduct_faq(self):
        self.assertView("conduct_faq")

    def test_conduct_reporting(self):
        self.assertView("conduct_reporting")

    def test_conduct_enforcement(self):
        self.assertView("conduct_enforcement")

    def test_conduct_changes(self):
        self.assertView("conduct_changes")

    def test_styleguide(self):
        self.assertView("styleguide")


class ExcludeHostsLocaleMiddlewareTests(TestCase):
    """
    djangoproject.middleware.ExcludeHostsLocaleMiddleware properly prevents
    the hosts in settings.LOCALE_MIDDLEWARE_EXCLUDED_HOSTS from being
    processed by django.middleware.locale.LocaleMiddleware, as evidenced by
    the presence or absence of 'Content-Language' and 'Vary' headers in the
    response.
    """

    docs_host = "docs.djangoproject.localhost"
    www_host = "www.djangoproject.localhost"

    @classmethod
    def setUpTestData(cls):
        r2 = Release.objects.create(version="2.0")
        DocumentRelease.objects.create(lang="en", release=r2, is_default=True)

    def test_docs_host_excluded(self):
        "We get no Content-Language or Vary headers when docs host is excluded"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host]):
            resp = self.client.get("/", headers={"host": self.docs_host})
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertNotIn("Content-Language", resp)
        self.assertNotIn("Vary", resp)

    def test_docs_host_with_port_excluded(self):
        """
        We get no Content-Language or Vary headers when docs host
        (with a port) is excluded
        """
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host]):
            resp = self.client.get("/", headers={"host": "%s:8000" % self.docs_host})
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertNotIn("Content-Language", resp)
        self.assertNotIn("Vary", resp)

    def test_docs_host_forwarded_excluded(self):
        """
        We get no Content-Language or Vary headers when docs host
        (via X-Forwarded_host) is excluded
        """
        with self.settings(
            LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host], USE_X_FORWARDED_HOST=True
        ):
            resp = self.client.get("/", headers={"x-forwarded-host": self.docs_host})
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertNotIn("Content-Language", resp)
        self.assertNotIn("Vary", resp)

    def test_docs_host_not_excluded(self):
        "We still get Content-Language when docs host is not excluded"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[]):
            resp = self.client.get("/", headers={"host": self.docs_host})
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertIn("Content-Language", resp)
        self.assertIn("Vary", resp)

    def test_www_host(self):
        "www should still use LocaleMiddleware"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host]):
            resp = self.client.get("/", headers={"host": self.www_host})
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn("Content-Language", resp)
        self.assertIn("Vary", resp)

    def test_www_host_with_port(self):
        "www (with a port) should still use LocaleMiddleware"
        with self.settings(LOCALE_MIDDLEWARE_EXCLUDED_HOSTS=[self.docs_host]):
            resp = self.client.get("/", headers={"host": "%s:8000" % self.www_host})
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn("Content-Language", resp)
        self.assertIn("Vary", resp)


# https://adamj.eu/tech/2024/06/23/django-test-pending-migrations/
class PendingMigrationsTests(TestCase):
    def test_no_pending_migrations(self):
        out = StringIO()
        try:
            call_command(
                "makemigrations",
                "--check",
                stdout=out,
                stderr=StringIO(),
            )
        except SystemExit:  # pragma: no cover
            raise AssertionError("Pending migrations:\n" + out.getvalue()) from None


class Header1Tests(TestCase):
    def extract_patterns(self, patterns, prefix="", urls=None):
        urls = urls or []
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                self.extract_patterns(
                    pattern.url_patterns, prefix + pattern.pattern.regex.pattern
                )
            elif hasattr(pattern, "pattern") and pattern.name:
                try:
                    urls.append(reverse(pattern.name))
                except NoReverseMatch:
                    pass  # Ignore URLs that require arguments.
        return urls

    def test_single_h1_per_page(self):
        excluded_urls = [
            "rss/",
            "styleguide/",  # Has multiple <h1> examples.
            "admin/",  # Admin templates are out of our control.
            "reset/done/",  # Uses an admin template.
        ]
        resolver = get_resolver()
        urls = self.extract_patterns(resolver.url_patterns)
        for url in urls:
            if all(url_substring not in url for url_substring in excluded_urls):
                with self.subTest(url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, "<h1", count=1)
