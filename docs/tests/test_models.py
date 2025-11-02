import datetime
from operator import attrgetter

from django.conf import settings
from django.db import connection
from django.test import TestCase

from releases.models import Release

from ..models import Document, DocumentRelease


class ModelsTests(TestCase):
    def test_scm_url(self):
        r = Release.objects.create(version="4.1", date=None)
        d = DocumentRelease.objects.create(release=r)
        self.assertEqual(
            d.scm_url,
            "https://github.com/django/django.git@stable/4.1.x",
        )

    def test_dev_is_supported(self):
        """
        Document without a release ("dev") is supported.
        """
        d = DocumentRelease.objects.create()

        self.assertTrue(d.is_supported)
        self.assertTrue(d.is_dev)
        self.assertFalse(d.is_preview)

    def test_preview_is_supported(self):
        """
        Document with a release without a date (alpha/beta/rc) is supported as
        "preview".
        """
        r = Release.objects.create(version="3.0", date=None)
        d = DocumentRelease.objects.create(release=r)

        self.assertTrue(d.is_supported)
        self.assertFalse(d.is_dev)
        self.assertTrue(d.is_preview)

    def test_current_is_supported(self):
        """
        Document with a release without an EOL date is supported.
        """
        today = datetime.date.today()
        day = datetime.timedelta(1)
        r = Release.objects.create(version="1.8", date=today - 5 * day)
        d = DocumentRelease.objects.create(release=r)

        self.assertTrue(d.is_supported)
        self.assertFalse(d.is_dev)
        self.assertFalse(d.is_preview)

    def test_previous_is_supported(self):
        """
        Document with a release with an EOL date in the future is supported.
        """
        today = datetime.date.today()
        day = datetime.timedelta(1)
        r = Release.objects.create(
            version="1.8", date=today - 5 * day, eol_date=today + 5 * day
        )
        d = DocumentRelease.objects.create(release=r)

        self.assertTrue(d.is_supported)
        self.assertFalse(d.is_dev)
        self.assertFalse(d.is_preview)

    def test_old_is_unsupported(self):
        """
        Document with a release with an EOL date in the past is insupported.
        """
        today = datetime.date.today()
        day = datetime.timedelta(1)
        r = Release.objects.create(
            version="1.8", date=today - 15 * day, eol_date=today - 5 * day
        )
        d = DocumentRelease.objects.create(release=r)

        self.assertFalse(d.is_supported)
        self.assertFalse(d.is_dev)
        self.assertFalse(d.is_preview)

    def test_most_recent_micro_release_considered(self):
        """
        Dates are looked up on the latest micro release in a given series.
        """
        today = datetime.date.today()
        day = datetime.timedelta(1)
        r = Release.objects.create(version="1.8", is_active=True, date=today - 15 * day)
        d = DocumentRelease.objects.create(release=r)
        r2 = Release.objects.create(version="1.8.1", date=today - 5 * day)

        # The EOL date is not set when the next release is not active.
        r.refresh_from_db()
        self.assertIsNone(r.eol_date)

        # The EOL date of the first release is set for published and newer releases.
        r2.is_active = True
        r2.save()
        r.refresh_from_db()
        self.assertEqual(r.eol_date, r2.date)

        # Since 1.8.1 is still supported, docs show up as supported.
        self.assertTrue(d.is_supported)
        self.assertFalse(d.is_dev)
        self.assertFalse(d.is_preview)


class ManagerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        r1 = Release.objects.create(version="1.0")
        r2 = Release.objects.create(version="2.0")
        DocumentRelease.objects.bulk_create(
            DocumentRelease(lang=lang, release=release)
            for lang, release in [
                ("en", None),
                ("en", r1),
                ("en", r2),
                ("sv", r1),
                ("ar", r1),
            ]
        )

    def test_by_version(self):
        self.assertQuerySetEqual(
            DocumentRelease.objects.by_version("1.0"),
            [("en", "1.0"), ("sv", "1.0"), ("ar", "1.0")],
            transform=attrgetter("lang", "version"),
            ordered=False,
        )

    def test_by_version_dev(self):
        self.assertQuerySetEqual(
            DocumentRelease.objects.by_version("dev"),
            [("en", "dev")],
            transform=attrgetter("lang", "version"),
            ordered=False,
        )

    def test_by_versions(self):
        self.assertQuerySetEqual(
            DocumentRelease.objects.by_versions("1.0", "dev"),
            [("en", "dev"), ("en", "1.0"), ("sv", "1.0"), ("ar", "1.0")],
            transform=attrgetter("lang", "version"),
            ordered=False,
        )

    def test_by_versions_empty(self):
        with self.assertRaises(ValueError):
            DocumentRelease.objects.by_versions()

    def test_get_by_version_and_lang_exists(self):
        doc = DocumentRelease.objects.get_by_version_and_lang("1.0", "en")
        self.assertEqual(doc.release.version, "1.0")
        self.assertEqual(doc.lang, "en")

    def test_get_by_version_and_lang_missing(self):
        with self.assertRaises(DocumentRelease.DoesNotExist):
            DocumentRelease.objects.get_by_version_and_lang("2.0", "sv")

    def test_get_available_languages_by_version(self):
        get = DocumentRelease.objects.get_available_languages_by_version
        self.assertEqual(list(get("1.0")), ["ar", "en", "sv"])
        self.assertEqual(list(get("2.0")), ["en"])
        self.assertEqual(list(get("3.0")), [])


class DocumentManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.release = DocumentRelease.objects.create(
            release=Release.objects.create(version="1.2.3"),
        )
        cls.release_fr = DocumentRelease.objects.create(lang="fr")
        documents = [
            {
                "metadata": {
                    "body": (
                        '<div class="section" id="s-generic-views">\n'
                        '<span id="generic-views"></span><h1>Generic views'
                        '<a class="headerlink" href="#generic-views" title='
                        '"Permalink to this headline">¶</a></h1>\n<p>See <a class='
                        '"reference internal" href="../../../ref/class-based-views/">'
                        '<span class="doc">Built-in class-based views API</span></a>.'
                        "</p>\n</div>\n"
                    ),
                    "breadcrumbs": [
                        {"path": "topics", "title": "Using Django"},
                        {"path": "topics/http", "title": "Handling HTTP requests"},
                    ],
                    "parents": "topics http",
                    "slug": "generic-views",
                    "title": "Generic views",
                    "toc": (
                        '<ul>\n<li><a class="reference internal" href="#">Generic views'
                        "</a></li>\n</ul>\n"
                    ),
                },
                "path": "topics/http/generic-views",
                "release": cls.release,
                "title": "Generic views",
            },
            {
                "metadata": {
                    "body": (
                        '<div class="section" id="s-django-1-2-1-release-notes">\n<span'
                        ' id="django-1-2-1-release-notes"></span><h1>Django 1.2.1 '
                        'release notes<a class="headerlink" href="#django-1-2-1-release'
                        '-notes" title="Permalink to this headline">¶</a></h1>\n'
                        "<p>Django 1.2.1 was released almost immediately after 1.2.0 to"
                        " correct two small\nbugs: one was in the documentation "
                        'packaging script, the other was a <a class="reference '
                        'external" href="https://code.djangoproject.com/ticket/13560">'
                        "bug</a> that\naffected datetime form field widgets when "
                        "localization was enabled.</p>\n</div>\n"
                    ),
                    "breadcrumbs": [
                        {"path": "releases", "title": "Release notes"},
                    ],
                    "parents": "releases",
                    "slug": "1.2.1",
                    "title": "Django 1.2.1 release notes",
                    "toc": (
                        '<ul>\n<li><a class="reference internal" href="#">Django 1.2.1 '
                        "release notes</a></li>\n</ul>\n"
                    ),
                },
                "path": "releases/1.2.1",
                "release": cls.release,
                "title": "Django 1.2.1 release notes",
            },
            {
                "metadata": {
                    "body": (
                        '<div class="section" id="s-django-1-9-4-release-notes">\n<span'
                        ' id="django-1-9-4-release-notes"></span><h1>Django 1.9.4 '
                        'release notes<a class="headerlink" href="#django-1-9-4-release'
                        '-notes" title="Permalink to this headline">¶</a></h1>\n<p><em>'
                        "March 5, 2016</em></p>\n<p>Django 1.9.4 fixes a regression on "
                        "Python 2 in the 1.9.3 security release\nwhere <code class="
                        '"docutils literal"><span class="pre">utils.http.is_safe_url()'
                        '</span></code> crashes on bytestring URLs (<a class="reference'
                        ' external" href="https://code.djangoproject.com/ticket/26308">'
                        "#26308</a>).</p>\n</div>\n"
                    ),
                    "breadcrumbs": [
                        {"path": "releases", "title": "Release notes"},
                    ],
                    "parents": "releases",
                    "slug": "1.9.4",
                    "title": "Django 1.9.4 release notes",
                    "toc": (
                        '<ul>\n<li><a class="reference internal" href="#">Django 1.9.4 '
                        "release notes</a></li>\n</ul>\n"
                    ),
                },
                "path": "releases/1.9.4",
                "release": cls.release,
                "title": "Django 1.9.4 release notes",
            },
            {
                "metadata": {
                    "body": (
                        '<div class="section" id="s-generic-views">\n<span id="generic'
                        '-views"></span><h1>Vues génériques<a class="headerlink" href='
                        '"#generic-views" title="Lien permanent vers ce titre">¶</a>'
                        '</h1>\n<p>Voir <a class="reference internal" href="../../../'
                        'ref/class-based-views/"><span class="doc">API des vues '
                        "intégrées fondées sur les classes.</span></a>.</p>\n</div>\n"
                    ),
                    "breadcrumbs": [
                        {"path": "topics", "title": "Using Django"},
                        {"path": "topics/http", "title": "Handling HTTP requests"},
                    ],
                    "parents": "topics http",
                    "slug": "generic-views",
                    "title": "Vues génériques",
                    "toc": (
                        '<ul>\n<li><a class="reference internal" href="#">Vues '
                        "génériques</a></li>\n</ul>\n"
                    ),
                },
                "path": "topics/http/generic-views",
                "release": cls.release_fr,
                "title": "Vues génériques",
            },
            {
                "metadata": {
                    "body": (
                        '<div class="section" id="s-django-1-2-1-release-notes">\n<span'
                        ' id="django-1-2-1-release-notes"></span><h1>Notes de '
                        'publication de Django 1.2.1<a class="headerlink" href="#django'
                        '-1-2-1-release-notes" title="Lien permanent vers ce titre">¶'
                        "</a></h1>\n<p>Django 1.2.1 was released almost immediately "
                        "after 1.2.0 to correct two small\nbugs: one was in the "
                        "documentation packaging script, the other was a <a class="
                        '"reference external" href="https://code.djangoproject.com/'
                        'ticket/13560">bug</a> that\naffected datetime form field '
                        "widgets when localization was enabled.</p>\n</div>\n"
                    ),
                    "breadcrumbs": [
                        {"path": "releases", "title": "Release notes"},
                    ],
                    "parents": "releases",
                    "slug": "1.2.1",
                    "title": "Notes de publication de Django 1.2.1",
                    "toc": (
                        '<ul>\n<li><a class="reference internal" href="#">Notes de '
                        "publication de Django 1.2.1</a></li>\n</ul>\n"
                    ),
                },
                "path": "releases/1.2.1",
                "release": cls.release_fr,
                "title": "Notes de publication de Django 1.2.1",
            },
            {
                "metadata": {
                    "body": (
                        '<div class="section" id="s-django-1-9-4-release-notes">\n<span'
                        ' id="django-1-9-4-release-notes"></span><h1>Notes de '
                        'publication de Django 1.9.4<a class="headerlink" href="#django'
                        '-1-9-4-release-notes" title="Lien permanent vers ce titre">¶'
                        "</a></h1>\n<p><em>March 5, 2016</em></p>\n<p>Django 1.9.4 "
                        "fixes a regression on Python 2 in the 1.9.3 security release\n"
                        'where <code class="docutils literal"><span class="pre">utils.'
                        "http.is_safe_url()</span></code> crashes on bytestring URLs "
                        '(<a class="reference external" href="https://code.'
                        'djangoproject.com/ticket/26308">#26308</a>).</p>\n</div>\n'
                    ),
                    "breadcrumbs": [
                        {"path": "releases", "title": "Release notes"},
                    ],
                    "parents": "releases",
                    "slug": "1.9.4",
                    "title": "Notes de publication de Django 1.9.4",
                    "toc": (
                        '<ul>\n<li><a class="reference internal" href="#">Notes de '
                        "publication de Django 1.9.4</a></li>\n</ul>\n"
                    ),
                },
                "path": "releases/1.9.4",
                "release": cls.release_fr,
                "title": "Notes de publication de Django 1.9.4",
            },
        ]
        Document.objects.bulk_create(Document(**doc) for doc in documents)

    def test_search(self):
        expected_list = [
            (
                "releases/1.2.1",
                "<mark>Django</mark> 1.2.1 release notes",  # Ranked: 0.96982837.
                (
                    "<mark>Django</mark> 1.2.1 release notes ¶  \n "
                    "<mark>Django</mark> 1.2.1 was released almost immediately after "
                    "1.2.0 to correct two small"
                ),
            ),
            (
                "releases/1.9.4",
                "<mark>Django</mark> 1.9.4 release notes",  # Ranked: 0.9490876.
                (
                    "<mark>Django</mark> 1.9.4 release notes ¶  \n  "
                    "March 5, 2016  \n "
                    "<mark>Django</mark> 1.9.4 fixes a regression on Python 2 in the "
                    "1.9.3 security"
                ),
            ),
        ]
        self.assertQuerySetEqual(
            Document.objects.search("django", self.release),
            expected_list,
            transform=attrgetter("path", "headline", "highlight"),
        )

    def test_websearch(self):
        self.assertQuerySetEqual(
            Document.objects.search('django "release notes" -packaging', self.release),
            ["Django 1.9.4 release notes"],
            transform=attrgetter("title"),
        )

    def test_multilingual_search(self):
        self.assertQuerySetEqual(
            Document.objects.search("publication", self.release_fr),
            [
                "Notes de publication de Django 1.2.1",  # Ranked: 1.0693262.
                "Notes de publication de Django 1.9.4",  # Ranked: 1.0458658.
            ],
            transform=attrgetter("title"),
        )

    def test_empty_search(self):
        self.assertSequenceEqual(Document.objects.search("", self.release), [])

    def test_search_breadcrumbs(self):
        doc = (
            Document.objects.filter(title="Generic views")
            .search("generic", self.release)
            .get()
        )
        self.assertEqual(
            doc.breadcrumbs,
            [
                {"path": "topics", "title": "Using Django"},
                {"path": "topics/http", "title": "Handling HTTP requests"},
            ],
        )

    def test_search_highlight_stemmed(self):
        # The issue only manifests itself when the defaut search config is not english
        with connection.cursor() as cursor:
            cursor.execute("SET default_text_search_config TO 'simple'", [])

        self.release.documents.create(
            config="english",
            path="/",
            title="triaging tickets",
            metadata={"body": "text containing the word triaging", "breadcrumbs": []},
        )

        self.assertQuerySetEqual(
            Document.objects.search("triaging", self.release),
            [
                (
                    "<mark>triaging</mark> tickets",
                    "text containing the word <mark>triaging</mark>",
                )
            ],
            transform=attrgetter("headline", "highlight"),
        )

    def test_search_title(self):
        misspelled_query = Document.objects.search("viewss", self.release)
        with self.assertNumQueries(1):
            self.assertQuerySetEqual(
                misspelled_query,
                [("Generic views", "en", "1.2.3")],
                transform=attrgetter(
                    "headline", "release.lang", "release.release.version"
                ),
            )


class UpdateDocTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.release = DocumentRelease.objects.create()

    def test_sync_to_db(self):
        self.release.sync_to_db(
            [
                {
                    "body": "This is the body",
                    "title": "This is the title",
                    "current_page_name": "foo/bar",
                }
            ]
        )
        document = self.release.documents.get()
        self.assertEqual(document.path, "foo/bar")

    def test_clean_path(self):
        self.release.sync_to_db(
            [
                {
                    "body": "This is the body",
                    "title": "This is the title",
                    "current_page_name": "foo/bar/index",
                }
            ]
        )
        document = self.release.documents.get()
        self.assertEqual(document.path, "foo/bar")

    def test_title_strip_tags(self):
        self.release.sync_to_db(
            [
                {
                    "body": "This is the body",
                    "title": "This is the <strong>title</strong>",
                    "current_page_name": "foo/bar",
                }
            ]
        )
        self.assertQuerySetEqual(
            self.release.documents.all(),
            ["This is the title"],
            transform=attrgetter("title"),
        )

    def test_title_entities(self):
        self.release.sync_to_db(
            [
                {
                    "body": "This is the body",
                    "title": "Title &amp; title",
                    "current_page_name": "foo/bar",
                }
            ]
        )
        self.assertQuerySetEqual(
            self.release.documents.all(),
            ["Title & title"],
            transform=attrgetter("title"),
        )

    def test_empty_documents(self):
        self.release.sync_to_db(
            [
                {"title": "Empty body document", "current_page_name": "foo/1"},
                {"body": "Empty title document", "current_page_name": "foo/2"},
                {"current_page_name": "foo/3"},
            ]
        )
        self.assertQuerySetEqual(self.release.documents.all(), [])

    def test_excluded_documents(self):
        """
        Documents aren't created for partially translated documents excluded
        from robots indexing.
        """
        # Read the first Disallow line of robots.txt.
        robots_path = settings.BASE_DIR.joinpath(
            "djangoproject", "static", "robots.docs.txt"
        )
        with open(str(robots_path)) as fh:
            for line in fh:
                if line.startswith("Disallow:"):
                    break
        _, lang, version, path = line.strip().split("/")

        release = DocumentRelease.objects.create(
            lang=lang,
            release=Release.objects.create(version=version),
        )
        release.sync_to_db(
            [
                {"body": "", "title": "", "current_page_name": "nonexcluded/bar"},
                {"body": "", "title": "", "current_page_name": "%s/bar" % path},
            ]
        )
        document = release.documents.get()
        self.assertEqual(document.path, "nonexcluded/bar")
