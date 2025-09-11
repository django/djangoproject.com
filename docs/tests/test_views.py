from http import HTTPStatus

from django.contrib.sites.models import Site
from django.test import SimpleTestCase, TestCase
from django.urls import reverse, set_urlconf
from django_hosts.resolvers import reverse as reverse_with_host

from djangoproject.urls import www as www_urls
from releases.models import Release

from ..models import Document, DocumentRelease
from ..search import DocumentationCategory
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
        cls.active_filter = '<a aria-current="page">'

        for category in DocumentationCategory:
            Document.objects.create(
                **{
                    "metadata": {
                        "body": "Generic Views",
                        "breadcrumbs": [
                            {"path": category.value, "title": str(category.label)},
                        ],
                        "parents": category.value,
                        "slug": "generic-views",
                        "title": "Generic views",
                        "toc": (
                            '<ul>\n<li><a class="reference internal" href="#">'
                            "Generic views</a></li>\n</ul>\n"
                        ),
                    },
                    "path": f"{category.value}/generic-views",
                    "release": cls.doc_release,
                    "title": "Generic views",
                }
            )

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

    def test_search_type_filter_all(self):
        response = self.client.get(
            "/en/5.1/search/?q=generic",
            headers={"host": "docs.djangoproject.localhost:8000"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "4 results for <em>generic</em> in version 5.1", html=True
        )
        self.assertContains(response, self.active_filter, count=1)
        self.assertContains(response, f"{self.active_filter}All</a>", html=True)

    def test_search_type_filter_by_doc_types(self):
        for category in DocumentationCategory:
            with self.subTest(category=category):
                response = self.client.get(
                    f"/en/5.1/search/?q=generic&category={category.value}",
                    headers={"host": "docs.djangoproject.localhost:8000"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    "Only 1 result for <em>generic</em> in version 5.1",
                    html=True,
                )
                self.assertContains(response, self.active_filter, count=1)
                self.assertContains(
                    response, f"{self.active_filter}{category.label}</a>", html=True
                )
                self.assertContains(response, '<a href="?q=generic">All</a>', html=True)

    def test_search_category_filter_invalid_doc_categories(self):
        response = self.client.get(
            "/en/5.1/search/?q=generic&category=invalid-so-ignored",
            headers={"host": "docs.djangoproject.localhost:8000"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "4 results for <em>generic</em> in version 5.1", html=True
        )
        self.assertContains(response, self.active_filter, count=1)
        self.assertContains(response, f"{self.active_filter}All</a>", html=True)

    def test_search_category_filter_no_results(self):
        response = self.client.get(
            "/en/5.1/search/?q=potato&category=ref",
            headers={"host": "docs.djangoproject.localhost:8000"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_filter, count=1)
        self.assertContains(
            response, f"{self.active_filter}API Reference</a>", html=True
        )
        self.assertContains(
            response, "0 results for <em>potato</em> in version 5.1", html=True
        )
        self.assertContains(
            response,
            'Please try searching <a href="?q=potato">all documentation results</a>.',
            html=True,
        )

    def test_code_links(self):
        queryset_data = {
            "metadata": {
                "body": (
                    "QuerySet API Reference QuerySet select_related selects related"
                    " things select_for_update selects things for update."
                ),
                "python_objects": {
                    "QuerySet": "django.db.models.query.QuerySet",
                    "QuerySet.select_related": (
                        "django.db.models.query.QuerySet.select_related"
                    ),
                    "QuerySet.select_for_update": (
                        "django.db.models.query.QuerySet.select_for_update"
                    ),
                },
                "python_objects_search": ("QuerySet select_related select_for_update"),
                "breadcrumbs": [{"path": "refs", "title": "API Reference"}],
                "parents": "API Reference",
                "slug": "query",
                "title": "QuerySet API Reference",
                "toc": (
                    '<ul>\n<li><a class="reference internal" href="#">QuerySet API'
                    " Reference</a></li>\n</ul>\n"
                ),
            },
            "path": "refs/query",
            "release": self.doc_release,
            "title": "QuerySet",
        }
        empty_page_data = {
            "metadata": {
                "body": "Empty page",
                "breadcrumbs": [{"path": "refs", "title": "API Reference"}],
                "parents": "API Reference",
                "slug": "empty",
                "title": "Empty page",
                "toc": (
                    '<ul>\n<li><a class="reference internal" href="#">Empty page'
                    "</a></li>\n</ul>\n"
                ),
            },
            "path": "refs/empty",
            "release": self.doc_release,
            "title": "Empty page",
        }
        Document.objects.bulk_create(
            [Document(**queryset_data), Document(**empty_page_data)]
        )
        base_url = reverse_with_host(
            "document-detail",
            host="docs",
            kwargs={"lang": "en", "version": "5.1", "url": "refs/query"},
        )
        for query, expected_code_links in [
            (
                "queryset",
                f'<ul class="code-links"><li><a href="{base_url}#django.db.models.query'
                '.QuerySet"><div><code>QuerySet</code><div class="meta">django.db.'
                "models.query</div></div></a></li></ul>",
            ),
            (
                "select",
                f'<ul class="code-links"><li><a href="{base_url}#django.db.models.query'
                '.QuerySet.select_for_update"><div><code>QuerySet.select_for_update'
                '</code><div class="meta">django.db.models.query</div></div></a></li>'
                f'<li><a href="{base_url}#django.db.models.query.QuerySet.'
                'select_related"><div><code>QuerySet.select_related</code><div '
                'class="meta">django.db.models.query</div></div></a></li></ul>',
            ),
        ]:
            with self.subTest(query=query):
                response = self.client.get(
                    f"/en/5.1/search/?q={query}",
                    headers={"host": "docs.djangoproject.localhost:8000"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    f"Only 1 result for <em>{query}</em> in version 5.1",
                    html=True,
                )
                self.assertContains(response, expected_code_links, html=True)


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
