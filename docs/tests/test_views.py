from http import HTTPStatus

from django.contrib.sites.models import Site
from django.test import SimpleTestCase, TestCase
from django.urls import reverse, set_urlconf
from django_hosts.resolvers import reverse as reverse_with_host

from djangoproject.urls import www as www_urls
from releases.models import Release

from ..models import Document, DocumentRelease
from ..sitemaps import DocsSitemap


class RedirectsTests(SimpleTestCase):
    @classmethod
    def tearDownClass(cls):
        # cleanup URLconfs changed by django-hosts
        set_urlconf(None)
        super().tearDownClass()

    def test_team_url(self):
        # This URL is linked from the docs.
        self.assertEqual(
            "/foundation/teams/", reverse("members:teams", urlconf=www_urls)
        )

    def test_internals_team(self):
        response = self.client.get(
            "/en/dev/internals/team/",
            headers={"host": "docs.djangoproject.localhost:8000"},
        )
        self.assertRedirects(
            response,
            "https://www.djangoproject.com/foundation/teams/",
            status_code=HTTPStatus.MOVED_PERMANENTLY,
            fetch_redirect_response=False,
        )


class SearchFormTestCase(TestCase):
    fixtures = ["doc_test_fixtures"]

    @classmethod
    def setUpTestData(cls):
        # We need to create an extra Site because docs have SITE_ID=2
        Site.objects.create(name="Django test", domain="example2.com")
        cls.release = Release.objects.create(version="5.1")
        cls.doc_release = DocumentRelease.objects.create(release=cls.release)

    @classmethod
    def tearDownClass(cls):
        # cleanup URLconfs changed by django-hosts
        set_urlconf(None)
        super().tearDownClass()

    def test_empty_get(self):
        response = self.client.get(
            "/en/dev/search/", headers={"host": "docs.djangoproject.localhost:8000"}
        )
        self.assertEqual(response.status_code, 200)


class SitemapTests(TestCase):
    fixtures = ["doc_test_fixtures"]

    @classmethod
    def tearDownClass(cls):
        # cleanup URLconfs changed by django-hosts
        set_urlconf(None)
        super().tearDownClass()

    def test_sitemap_index(self):
        response = self.client.get(
            "/sitemap.xml", headers={"host": "docs.djangoproject.localhost:8000"}
        )
        self.assertContains(response, "<sitemap>", count=2)
        en_sitemap_url = reverse_with_host(
            "document-sitemap", host="docs", kwargs={"section": "en"}
        )
        self.assertContains(response, f"<loc>{en_sitemap_url}</loc>")

    def test_sitemap(self):
        doc_release = DocumentRelease.objects.create()
        document = Document.objects.create(release=doc_release)
        sitemap = DocsSitemap("en")
        urls = sitemap.get_urls()
        self.assertEqual(len(urls), 1)
        url_info = urls[0]
        self.assertEqual(url_info["location"], document.get_absolute_url())

    def test_sitemap_404(self):
        response = self.client.get(
            "/sitemap-xx.xml", headers={"host": "docs.djangoproject.localhost:8000"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.context["exception"], "No sitemap available for section: 'xx'"
        )
