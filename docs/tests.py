import datetime
import os
from http import HTTPStatus
from operator import attrgetter
from pathlib import Path

from django.conf import settings
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse, set_urlconf

from djangoproject.urls import www as www_urls
from releases.models import Release

from .models import Document, DocumentRelease
from .search import DOCUMENT_SEARCH_VECTOR
from .sitemaps import DocsSitemap
from .utils import get_doc_path


class ModelsTests(TestCase):

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
        r = Release.objects.create(version='3.0', date=None)
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
        r = Release.objects.create(version='1.8',
                                   date=today - 5 * day)
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
        r = Release.objects.create(version='1.8',
                                   date=today - 5 * day,
                                   eol_date=today + 5 * day)
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
        r = Release.objects.create(version='1.8',
                                   date=today - 15 * day,
                                   eol_date=today - 5 * day)
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
        r = Release.objects.create(version='1.8',
                                   date=today - 15 * day)
        d = DocumentRelease.objects.create(release=r)
        r2 = Release.objects.create(version='1.8.1',
                                    date=today - 5 * day)

        # The EOL date of the first release is set automatically.
        r.refresh_from_db()
        self.assertEqual(r.eol_date, r2.date)

        # Since 1.8.1 is still supported, docs show up as supported.
        self.assertTrue(d.is_supported)
        self.assertFalse(d.is_dev)
        self.assertFalse(d.is_preview)


class ManagerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        r1 = Release.objects.create(version='1.0')
        r2 = Release.objects.create(version='2.0')
        DocumentRelease.objects.bulk_create(
            DocumentRelease(lang=lang, release=release)
            for lang, release in [('en', r1), ('en', r2), ('sv', r1), ('ar', r1)]
        )

    def test_by_version(self):
        doc_releases = DocumentRelease.objects.by_version('1.0')
        self.assertEqual(
            {(r.lang, r.release.version) for r in doc_releases},
            {('en', '1.0'), ('sv', '1.0'), ('ar', '1.0')}
        )

    def test_get_by_version_and_lang_exists(self):
        doc = DocumentRelease.objects.get_by_version_and_lang('1.0', 'en')
        self.assertEqual(doc.release.version, '1.0')
        self.assertEqual(doc.lang, 'en')

    def test_get_by_version_and_lang_missing(self):
        with self.assertRaises(DocumentRelease.DoesNotExist):
            DocumentRelease.objects.get_by_version_and_lang('2.0', 'sv')

    def test_get_available_languages_by_version(self):
        get = DocumentRelease.objects.get_available_languages_by_version
        self.assertEqual(list(get('1.0')), ['ar', 'en', 'sv'])
        self.assertEqual(list(get('2.0')), ['en'])
        self.assertEqual(list(get('3.0')), [])


class RedirectsTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        # cleanup URLconfs changed by django-hosts
        set_urlconf(None)
        super().tearDownClass()

    def test_team_url(self):
        # This URL is linked from the docs.
        self.assertEqual('/foundation/teams/', reverse('members:teams', urlconf=www_urls))

    def test_internals_team(self):
        response = self.client.get(
            '/en/dev/internals/team/',
            HTTP_HOST='docs.djangoproject.localhost:8000',
        )
        self.assertRedirects(
            response,
            'https://www.djangoproject.com/foundation/teams/',
            status_code=HTTPStatus.MOVED_PERMANENTLY,
            fetch_redirect_response=False,
        )


class SearchFormTestCase(TestCase):
    fixtures = ['doc_test_fixtures']

    def setUp(self):
        # We need to create an extra Site because docs have SITE_ID=2
        Site.objects.create(name='Django test', domain="example2.com")

    @classmethod
    def tearDownClass(cls):
        # cleanup URLconfs changed by django-hosts
        set_urlconf(None)
        super().tearDownClass()

    def test_empty_get(self):
        response = self.client.get('/en/dev/search/', HTTP_HOST='docs.djangoproject.localhost:8000')
        self.assertEqual(response.status_code, 200)


class TemplateTagTests(TestCase):

    def test_pygments_template_tag(self):
        template = Template('''
{% load docs %}
{% pygment 'python' %}
def band_listing(request):
    """A view of all bands."""
    bands = models.Band.objects.all()
    return render(request, 'bands/band_listing.html', {'bands': bands})

{% endpygment %}
''')
        self.assertHTMLEqual(
            template.render(Context()),
            """
            <div class="highlight">
                <pre>
                    <span></span>
                    <span class="k">def</span><span class="nf">band_listing</span>
                    <span class="p">(</span><span class="n">request</span>
                    <span class="p">):</span>
                    <span class="sd">&quot;&quot;&quot;A view of all bands.&quot;&quot;&quot;</span>
                    <span class="n">bands</span> <span class="o">=</span>
                    <span class="n">models</span><span class="o">.</span>
                    <span class="n">Band</span><span class="o">.</span>
                    <span class="n">objects</span><span class="o">.</span>
                    <span class="n">all</span><span class="p">()</span>
                    <span class="k">return</span> <span class="n">render</span>
                    <span class="p">(</span><span class="n">request</span>
                    <span class="p">,</span>
                    <span class="s1">&#39;bands/band_listing.html&#39;</span>
                    <span class="p">,</span> <span class="p">{</span>
                    <span class="s1">&#39;bands&#39;</span><span class="p">:</span>
                    <span class="n">bands</span><span class="p">})</span>
                </pre>
            </div>
            """
        )


class TestUtils(TestCase):
    def test_get_doc_path(self):
        # non-existent file
        self.assertEqual(get_doc_path(Path('root'), 'subpath.txt'), None)

        # existing file
        path, filename = __file__.rsplit(os.path.sep, 1)
        self.assertEqual(get_doc_path(Path(path), filename), None)


class UpdateDocTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.release = DocumentRelease.objects.create()

    def test_sync_to_db(self):
        self.release.sync_to_db([{
            'body': 'This is the body',
            'title': 'This is the title',
            'current_page_name': 'foo/bar',
        }])
        self.assertQuerysetEqual(self.release.documents.all(), ['<Document: en/dev/foo/bar>'])

    def test_clean_path(self):
        self.release.sync_to_db([{
            'body': 'This is the body',
            'title': 'This is the title',
            'current_page_name': 'foo/bar/index',
        }])
        self.assertQuerysetEqual(self.release.documents.all(), ['<Document: en/dev/foo/bar>'])

    def test_title_strip_tags(self):
        self.release.sync_to_db([{
            'body': 'This is the body',
            'title': 'This is the <strong>title</strong>',
            'current_page_name': 'foo/bar',
        }])
        self.assertQuerysetEqual(self.release.documents.all(), ['This is the title'], transform=attrgetter('title'))

    def test_title_entities(self):
        self.release.sync_to_db([{
            'body': 'This is the body',
            'title': 'Title &amp; title',
            'current_page_name': 'foo/bar',
        }])
        self.assertQuerysetEqual(self.release.documents.all(), ['Title & title'], transform=attrgetter('title'))

    def test_empty_documents(self):
        self.release.sync_to_db([
            {'title': 'Empty body document', 'current_page_name': 'foo/1'},
            {'body': 'Empty title document', 'current_page_name': 'foo/2'},
            {'current_page_name': 'foo/3'},
        ])
        self.assertQuerysetEqual(self.release.documents.all(), [])

    def test_excluded_documents(self):
        """
        Documents aren't created for partially translated documents excluded
        from robots indexing.
        """
        # Read the first Disallow line of robots.txt.
        robots_path = settings.BASE_DIR.joinpath('djangoproject', 'static', 'robots.docs.txt')
        with open(str(robots_path), 'r') as fh:
            for line in fh:
                if line.startswith("Disallow:"):
                    break
        _, lang, version, path = line.strip().split('/')

        release = DocumentRelease.objects.create(
            lang=lang, release=Release.objects.create(version=version),
        )
        release.sync_to_db([
            {'body': '', 'title': '', 'current_page_name': 'nonexcluded/bar'},
            {'body': '', 'title': '', 'current_page_name': '%s/bar' % path},
        ])
        self.assertQuerysetEqual(
            release.documents.all(),
            ['<Document: %s/%s/nonexcluded/bar>' % (lang, version)]
        )


class SitemapTests(TestCase):
    fixtures = ['doc_test_fixtures']

    @classmethod
    def tearDownClass(cls):
        # cleanup URLconfs changed by django-hosts
        set_urlconf(None)
        super().tearDownClass()

    def test_sitemap_index(self):
        response = self.client.get('/sitemap.xml', HTTP_HOST='docs.djangoproject.localhost:8000')
        self.assertContains(response, '<sitemap>', count=2)
        self.assertContains(response, '<loc>http://docs.djangoproject.localhost:8000/sitemap-en.xml</loc>')

    def test_sitemap(self):
        doc_release = DocumentRelease.objects.create()
        document = Document.objects.create(release=doc_release)
        sitemap = DocsSitemap('en')
        urls = sitemap.get_urls()
        self.assertEqual(len(urls), 1)
        url_info = urls[0]
        self.assertEqual(url_info['location'], document.get_absolute_url())

    def test_sitemap_404(self):
        response = self.client.get('/sitemap-xx.xml', HTTP_HOST='docs.djangoproject.localhost:8000')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.context['exception'],
            "No sitemap available for section: 'xx'"
        )


class DocumentManagerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.release = DocumentRelease.objects.create()
        cls.release_fr = DocumentRelease.objects.create(lang='fr')
        documents = [
            {
                'metadata': {
                    'body': (
                        '<div class="section" id="s-generic-views">\n<span id="generic-views"></span>'
                        '<h1>Generic views<a class="headerlink" href="#generic-views" title="Permalink to this headline">¶</a></h1>\n'
                        '<p>See <a class="reference internal" href="../../../ref/class-based-views/">'
                        '<span class="doc">Built-in class-based views API</span></a>.</p>\n</div>\n'
                    ),
                    'breadcrumbs': [],
                    'parents': 'topics http',
                    'slug': 'generic-views',
                    'title': 'Generic views',
                    'toc': '<ul>\n<li><a class="reference internal" href="#">Generic views</a></li>\n</ul>\n'
                },
                'path': 'topics/http/generic-views',
                'release': cls.release,
                'title': 'Generic views',
            },
            {
                'metadata': {
                    'body': (
                        '<div class="section" id="s-django-1-2-1-release-notes">\n<span id="django-1-2-1-release-notes"></span>'
                        '<h1>Django 1.2.1 release notes<a class="headerlink" href="#django-1-2-1-release-notes" title="Permalink to this headline">¶</a></h1>\n'
                        '<p>Django 1.2.1 was released almost immediately after 1.2.0 to correct two small\n'
                        'bugs: one was in the documentation packaging script, the other was a '
                        '<a class="reference external" href="https://code.djangoproject.com/ticket/13560">bug</a> that\n'
                        'affected datetime form field widgets when localization was enabled.</p>\n</div>\n'
                    ),
                    'breadcrumbs': [],
                    'parents': 'releases',
                    'slug': '1.2.1',
                    'title': 'Django 1.2.1 release notes',
                    'toc': '<ul>\n<li><a class="reference internal" href="#">Django 1.2.1 release notes</a></li>\n</ul>\n'
                },
                'path': 'releases/1.2.1',
                'release': cls.release,
                'title': 'Django 1.2.1 release notes'
            },
            {
                'metadata': {
                    'body': (
                        '<div class="section" id="s-django-1-9-4-release-notes">\n<span id="django-1-9-4-release-notes"></span>'
                        '<h1>Django 1.9.4 release notes<a class="headerlink" href="#django-1-9-4-release-notes" title="Permalink to this headline">¶</a></h1>\n'
                        '<p><em>March 5, 2016</em></p>\n<p>Django 1.9.4 fixes a regression on Python 2 in the 1.9.3 security release\n'
                        'where <code class="docutils literal"><span class="pre">utils.http.is_safe_url()</span></code> crashes on bytestring URLs '
                        '(<a class="reference external" href="https://code.djangoproject.com/ticket/26308">#26308</a>).</p>\n</div>\n'
                    ),
                    'breadcrumbs': [],
                    'parents': 'releases',
                    'slug': '1.9.4',
                    'title': 'Django 1.9.4 release notes',
                    'toc': '<ul>\n<li><a class="reference internal" href="#">Django 1.9.4 release notes</a></li>\n</ul>\n'
                },
                'path': 'releases/1.9.4',
                'release': cls.release,
                'title': 'Django 1.9.4 release notes'
            },
            {
                'metadata': {
                    'body': (
                        '<div class="section" id="s-generic-views">\n<span id="generic-views"></span>'
                        '<h1>Vues génériques<a class="headerlink" href="#generic-views" title="Lien permanent vers ce titre">¶</a></h1>\n'
                        '<p>Voir <a class="reference internal" href="../../../ref/class-based-views/">'
                        '<span class="doc">API des vues intégrées fondées sur les classes.</span></a>.</p>\n</div>\n'
                    ),
                    'breadcrumbs': [],
                    'parents': 'topics http',
                    'slug': 'generic-views',
                    'title': 'Vues génériques',
                    'toc': '<ul>\n<li><a class="reference internal" href="#">Vues génériques</a></li>\n</ul>\n'
                },
                'path': 'topics/http/generic-views',
                'release': cls.release_fr,
                'title': 'Vues génériques',
            },
            {
                'metadata': {
                    'body': (
                        '<div class="section" id="s-django-1-2-1-release-notes">\n<span id="django-1-2-1-release-notes"></span>'
                        '<h1>Notes de publication de Django 1.2.1'
                        '<a class="headerlink" href="#django-1-2-1-release-notes" title="Lien permanent vers ce titre">¶</a></h1>\n'
                        '<p>Django 1.2.1 was released almost immediately after 1.2.0 to correct two small\n'
                        'bugs: one was in the documentation packaging script, the other was a '
                        '<a class="reference external" href="https://code.djangoproject.com/ticket/13560">bug</a> that\n'
                        'affected datetime form field widgets when localization was enabled.</p>\n</div>\n'
                    ),
                    'breadcrumbs': [],
                    'parents': 'releases',
                    'slug': '1.2.1',
                    'title': 'Notes de publication de Django 1.2.1',
                    'toc': '<ul>\n<li><a class="reference internal" href="#">Notes de publication de Django 1.2.1</a></li>\n</ul>\n',
                },
                'path': 'releases/1.2.1',
                'release': cls.release_fr,
                'title': 'Notes de publication de Django 1.2.1',
            },
            {
                'metadata': {
                    'body': (
                        '<div class="section" id="s-django-1-9-4-release-notes">\n<span id="django-1-9-4-release-notes"></span>'
                        '<h1>Notes de publication de Django 1.9.4'
                        '<a class="headerlink" href="#django-1-9-4-release-notes" title="Lien permanent vers ce titre">¶</a></h1>\n'
                        '<p><em>March 5, 2016</em></p>\n<p>Django 1.9.4 fixes a regression on Python 2 in the 1.9.3 security release\n'
                        'where <code class="docutils literal"><span class="pre">utils.http.is_safe_url()</span></code> crashes on bytestring URLs '
                        '(<a class="reference external" href="https://code.djangoproject.com/ticket/26308">#26308</a>).</p>\n</div>\n'
                    ),
                    'breadcrumbs': [],
                    'parents': 'releases',
                    'slug': '1.9.4',
                    'title': 'Notes de publication de Django 1.9.4',
                    'toc': '<ul>\n<li><a class="reference internal" href="#">Notes de publication de Django 1.9.4</a></li>\n</ul>\n',
                },
                'path': 'releases/1.9.4',
                'release': cls.release_fr,
                'title': 'Notes de publication de Django 1.9.4',
            }
        ]
        Document.objects.bulk_create(((Document(**doc) for doc in documents)))
        Document.objects.update(search=DOCUMENT_SEARCH_VECTOR)

    def test_search(self):
        query_text = 'django'
        document_queryset = Document.objects.search(query_text, self.release).values_list('title', 'rank')
        document_list = [('Django 1.2.1 release notes', 0.969828), ('Django 1.9.4 release notes', 0.949088)]
        self.assertSequenceEqual(list(document_queryset), document_list)

    def test_multilingual_search(self):
        query_text = 'publication'
        queryset = Document.objects.search(query_text, self.release_fr).values_list('title', 'rank')
        self.assertSequenceEqual(queryset, [
            ('Notes de publication de Django 1.2.1', 1.06933),
            ('Notes de publication de Django 1.9.4', 1.04587),
        ])

    def test_empty_search(self):
        self.assertSequenceEqual(Document.objects.search('', self.release), [])
