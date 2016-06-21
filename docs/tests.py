import datetime
import os
from operator import attrgetter
from pathlib import Path

from django.contrib.sites.models import Site
from django.template import Context, Template
from django.test import TestCase
from django.urls import set_urlconf

from releases.models import Release

from .models import Document, DocumentRelease
from .sitemaps import DocsSitemap
from .utils import get_doc_path


class ModelsTests(TestCase):

    def test_dev_is_supported(self):
        """
        Document for a release without a date ("dev") is supported.
        """
        d = DocumentRelease.objects.create()

        self.assertTrue(d.is_supported)
        self.assertTrue(d.is_dev)

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


class ManagerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        r1 = Release.objects.create(version='1.0')
        r2 = Release.objects.create(version='2.0')
        DocumentRelease.objects.bulk_create(
            DocumentRelease(lang=lang, release=release)
            for lang, release in [('en', r1), ('en', r2), ('sv', r1)]
        )

    def test_by_version(self):
        doc_releases = DocumentRelease.objects.by_version('1.0')
        self.assertEqual(
            {(r.lang, r.release.version) for r in doc_releases},
            {('en', '1.0'), ('sv', '1.0')}
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
        self.assertEqual(set(get('1.0')), {'en', 'sv'})
        self.assertEqual(set(get('2.0')), {'en'})
        self.assertEqual(set(get('3.0')), set())


class SearchFormTestCase(TestCase):
    fixtures = ['doc_test_fixtures']

    def setUp(self):
        # We need to create an extra Site because docs have SITE_ID=2
        Site.objects.create(name='Django test', domain="example2.com")

    @classmethod
    def tearDownClass(cls):
        # cleanup URLconfs changed by django-hosts
        set_urlconf(None)
        super(SearchFormTestCase, cls).tearDownClass()

    def test_empty_get(self):
        response = self.client.get('/en/dev/search/',
                                   HTTP_HOST='docs.djangoproject.dev:8000')
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


class SitemapTests(TestCase):

    def test_sitemap(self):
        doc_release = DocumentRelease.objects.create()
        document = Document.objects.create(release=doc_release)
        sitemap = DocsSitemap()
        urls = sitemap.get_urls()
        self.assertEqual(len(urls), 1)
        url_info = urls[0]
        self.assertEqual(url_info['location'], document.get_absolute_url())
