import unittest
from http import HTTPStatus

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import SimpleTestCase, TestCase
from django.urls import reverse, set_urlconf
from django.utils.translation import activate, gettext as _
from django_hosts.resolvers import reverse as reverse_with_host, reverse_host

from djangoproject.urls import docs as docs_urls, www as www_urls
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
            headers={"host": reverse_host("docs")},
        )
        self.assertRedirects(
            response,
            "https://www.djangoproject.com/foundation/teams/",
            status_code=HTTPStatus.MOVED_PERMANENTLY,
            fetch_redirect_response=False,
        )

    def test_redirect_index_view(self):
        response = self.client.get(
            "/en/dev/index/",  # Route without name
            headers={"host": reverse_host("docs")},
        )
        self.assertRedirects(response, "/en/dev/", fetch_redirect_response=False)


class LangAndReleaseRedirectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.release = Release.objects.create(version="5.2")
        cls.doc_release = DocumentRelease.objects.create(
            release=cls.release, is_default=True
        )

    def test_index_view_redirect_to_current_document_release(self):
        response = self.client.get(
            reverse_with_host("homepage", host="docs"),
            headers={"host": reverse_host("docs")},
        )
        self.assertRedirects(
            response, self.doc_release.get_absolute_url(), fetch_redirect_response=False
        )

    def test_language_view_redirect_to_current_document_release_with_the_same_language(
        self,
    ):
        fr_doc_release = DocumentRelease.objects.create(release=self.release, lang="fr")
        response = self.client.get(
            "/fr/",  # Route without name
            headers={"host": reverse_host("docs")},
        )
        self.assertRedirects(
            response, fr_doc_release.get_absolute_url(), fetch_redirect_response=False
        )

    def test_stable_view_redirect_to_current_document_release(self):
        response = self.client.get(
            reverse_with_host(
                # The stable view doesn't have a name but it's basically
                # the document-detail route with a version set to "stable"
                "document-detail",
                kwargs={
                    "version": "stable",
                    "lang": self.doc_release.lang,
                    "url": "intro",
                },
                host="docs",
            ),
            headers={"host": reverse_host("docs")},
        )
        # Using Django's `reverse()` over django-hosts's `reverse_host()` as the later
        # one return an absolute URL but the view redirect only using the path component
        expected_url = reverse(
            # The stable view route doesn't have a name but it's basically
            # the `document-detail` route with a version set to "stable"
            "document-detail",
            kwargs={
                "version": self.doc_release.version,
                "lang": self.doc_release.lang,
                "url": "intro",
            },
            urlconf=docs_urls,
        )
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)


class DocumentViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc_release = DocumentRelease.objects.create(is_default=True)

    def test_document_index_view(self):
        # Set up a release so we aren't in `dev` version
        self.doc_release.release = Release.objects.create(version="5.2")
        self.doc_release.save(update_fields=["release"])

        response = self.client.get(
            reverse_with_host(
                "document-index",
                kwargs={
                    "lang": self.doc_release.lang,
                    "version": self.doc_release.version,
                },
                host="docs",
            ),
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("docurl"), "")
        self.assertEqual(
            response.context.get("rtd_version"), f"{self.doc_release.version}.x"
        )
        # Check the header used for Fastly
        self.assertEqual(response.headers.get("Surrogate-Control"), "max-age=604800")

    def test_document_index_view_with_dev_version(self):
        response = self.client.get(
            reverse_with_host(
                "document-index",
                kwargs={"lang": self.doc_release.lang, "version": "dev"},
                host="docs",
            ),
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("rtd_version"), "latest")

    @unittest.expectedFailure
    def test_document_index_view_with_stable_version(self):
        response = self.client.get(
            reverse_with_host(
                "document-index",
                kwargs={"lang": self.doc_release.lang, "version": "stable"},
                host="docs",
            ),
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("rtd_version"), "latest")

    def test_document_detail_view(self):
        response = self.client.get(
            reverse_with_host(
                "document-detail",
                kwargs={
                    "lang": self.doc_release.lang,
                    "version": "dev",
                    "url": "intro",
                },
                host="docs",
            ),
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("docurl"), "intro")
        # Check the header used for Fastly
        self.assertEqual(response.headers.get("Surrogate-Control"), "max-age=604800")


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
            "/en/dev/search/", headers={"host": reverse_host("docs")}
        )
        self.assertEqual(response.status_code, 200)
        # No header item is active.
        self.assertNotContains(response, '<li class="active">')
        # The search result page does not have the Documentation banner.
        self.assertNotContains(response, '<div class="copy-banner">')

    def test_search_type_filter_all(self):
        response = self.client.get(
            "/en/5.1/search/?q=generic",
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5 results for <em>generic</em>", html=True)
        self.assertContains(response, self.active_filter, count=1)
        self.assertContains(response, f"{self.active_filter}All</a>", html=True)

    def test_search_type_filter_by_doc_types(self):
        for category in DocumentationCategory:
            with self.subTest(category=category):
                response = self.client.get(
                    f"/en/5.1/search/?q=generic&category={category.value}",
                    headers={"host": reverse_host("docs")},
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    "1 result for <em>generic</em>",
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
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5 results for <em>generic</em>", html=True)
        self.assertContains(response, self.active_filter, count=1)
        self.assertContains(response, f"{self.active_filter}All</a>", html=True)

    def test_search_category_filter_no_results(self):
        response = self.client.get(
            "/en/5.1/search/?q=potato&category=ref",
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_filter, count=1)
        self.assertContains(
            response, f"{self.active_filter}API Reference</a>", html=True
        )
        self.assertContains(response, "0 results for <em>potato</em>", html=True)
        self.assertContains(
            response,
            'Please try searching <a href="?q=potato">all results</a>.',
            html=True,
        )

    def test_search_website_category_french(self):
        DocumentRelease.objects.create(release=self.release, lang="fr")
        response = self.client.get(
            "/fr/5.1/search/?q=potato&category=website",
            headers={"host": "docs.djangoproject.localhost:8000"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_filter, count=1)
        activate("fr")
        self.assertContains(
            response, f"{self.active_filter}{_('Django Website')}</a>", html=True
        )
        self.assertContains(
            response,
            _("The website content can only be searched in English."),
            html=True,
        )

    def test_search_category_filter_preserved(self):
        response = self.client.get(
            "/en/5.1/search/?q=potato&category=ref",
            headers={"host": "docs.djangoproject.localhost:8000"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<input type="hidden" name="category" value="ref">'
        )
        self.assertContains(
            response, f"{self.active_filter}API Reference</a>", html=True
        )
        response = self.client.post(
            "/en/5.1/search/?q=potato&category=ref",
            headers={"host": "docs.djangoproject.localhost:8000"},
            data={"category": "ref", "q": "fish"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<input type="hidden" name="category" value="ref">'
        )
        self.assertContains(
            response, f"{self.active_filter}API Reference</a>", html=True
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
            kwargs={
                "lang": settings.DEFAULT_LANGUAGE_CODE,
                "version": "5.1",
                "url": "refs/query",
            },
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
                    headers={"host": reverse_host("docs")},
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    f"1 result for <em>{query}</em>",
                    html=True,
                )
                self.assertContains(response, expected_code_links, html=True)


class SearchRedirectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc_release = DocumentRelease.objects.create(is_default=True)

    def test_redirect_search_view(self):
        # With a `q` parameters
        response = self.client.get(
            "/search/?q=django", headers={"host": reverse_host("docs")}
        )
        self.assertRedirects(
            response,
            "http://" + reverse_host("docs") + "/en/dev/search/?q=django",
            fetch_redirect_response=False,
        )

        # Without a `q` parameters
        response = self.client.get("/search/", headers={"host": reverse_host("docs")})
        self.assertRedirects(
            response,
            "http://" + reverse_host("docs") + "/en/dev/search/",
            fetch_redirect_response=False,
        )


class SitemapTests(TestCase):
    fixtures = ["doc_test_fixtures"]

    @classmethod
    def tearDownClass(cls):
        # cleanup URLconfs changed by django-hosts
        set_urlconf(None)
        super().tearDownClass()

    def test_sitemap_index(self):
        response = self.client.get(
            "/sitemap.xml", headers={"host": reverse_host("docs")}
        )
        self.assertContains(response, "<sitemap>", count=2)
        en_sitemap_url = reverse_with_host(
            "document-sitemap",
            host="docs",
            kwargs={"section": settings.DEFAULT_LANGUAGE_CODE},
        )
        self.assertContains(response, f"<loc>{en_sitemap_url}</loc>")

    def test_sitemap(self):
        doc_release = DocumentRelease.objects.create()
        document = Document.objects.create(
            release=doc_release,
            metadata={"parents": DocumentationCategory.TOPICS},
        )
        Document.objects.create(
            release=doc_release,
            metadata={"parents": DocumentationCategory.WEBSITE},
            path="example",
        )
        sitemap = DocsSitemap(settings.DEFAULT_LANGUAGE_CODE)
        urls = sitemap.get_urls()
        self.assertEqual(len(urls), 1)
        url_info = urls[0]
        self.assertEqual(url_info["location"], document.get_absolute_url())

    def test_sitemap_404(self):
        response = self.client.get(
            "/sitemap-xx.xml", headers={"host": reverse_host("docs")}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.context["exception"], "No sitemap available for section: 'xx'"
        )


class OpenSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc_release = DocumentRelease.objects.create(
            release=Release.objects.create(version="5.2"), is_default=True
        )

    def test_search_suggestions_view(self):
        # Without `q` parameter
        response = self.client.get(
            reverse_with_host(
                "document-search-suggestions",
                kwargs={
                    "lang": self.doc_release.lang,
                    "version": self.doc_release.version,
                },
                host="docs",
            ),
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.json(), [])

        # With `q` parameter but no Document
        response = self.client.get(
            reverse_with_host(
                "document-search-suggestions",
                kwargs={
                    "lang": self.doc_release.lang,
                    "version": self.doc_release.version,
                },
                host="docs",
            )
            + "?q=test",
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.json(), ["test", [], [], []])

        # # With `q` parameter and a Document
        document = Document.objects.create(
            release=self.doc_release,
            path="test-document",
            title="test title",
        )
        response = self.client.get(
            reverse_with_host(
                "document-search-suggestions",
                kwargs={
                    "lang": self.doc_release.lang,
                    "version": self.doc_release.version,
                },
                host="docs",
            )
            + "?q=test",
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(
            response.json(),
            [
                "test",
                ["test title"],
                [],
                [
                    reverse_with_host(
                        "contenttypes-shortcut",
                        kwargs={
                            "content_type_id": ContentType.objects.get_for_model(
                                Document
                            ).pk,
                            "object_id": document.id,
                        },
                    )
                ],
            ],
        )

    def test_search_description(self):
        response = self.client.get(
            reverse_with_host(
                "document-search-description",
                kwargs={
                    "lang": self.doc_release.lang,
                    "version": self.doc_release.version,
                },
                host="docs",
            ),
            headers={"host": reverse_host("docs")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-Type"], "application/opensearchdescription+xml"
        )
        self.assertTemplateUsed("docs/search_description.html")
        self.assertContains(response, f"<Language>{self.doc_release.lang}</Language>")
