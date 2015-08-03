import os
from pathlib import Path

from django.contrib.sites.models import Site
from django.core.urlresolvers import set_urlconf
from django.http.request import HttpRequest
from django.template import Context, Template
from django.test import TestCase

from .utils import get_doc_path


class SearchFormTestCase(TestCase):
    fixtures = ['doc_test_fixtures']

    def setUp(self):
        # We need to create an extra Site because docs have SITE_ID=2
        Site.objects.create(name='Django test', domain="example.com")

    @classmethod
    def tearDownClass(cls):
        # cleanup URLconfs changed by django-hosts
        set_urlconf(None)
        super(SearchFormTestCase, cls).tearDownClass()

    def test_empty_get(self):
        response = self.client.get('/en/dev/search/',
                                   HTTP_HOST='docs.djangoproject.dev:8000')
        self.assertEqual(response.status_code, 200)

    def test_search_form_templatetag(self):
        template = Template('{% load docs %}{% search_form %}')
        self.assertIn(
            '1.4',
            template.render(Context({'lang': 'en', 'version': 'stable', 'request': HttpRequest()})),
        )


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
        self.assertEqual(
            template.render(Context()),
            "\n\n<div class=\"highlight\"><pre><span class=\"k\">def</span> <span class=\"nf\">"
            "band_listing</span><span class=\"p\">(</span><span class=\"n\">request</span><span "
            "class=\"p\">):</span>\n    <span class=\"sd\">&quot;&quot;&quot;A view of all bands"
            ".&quot;&quot;&quot;</span>\n    <span class=\"n\">bands</span> <span class=\"o\">="
            "</span> <span class=\"n\">models</span><span class=\"o\">.</span><span class=\"n\">"
            "Band</span><span class=\"o\">.</span><span class=\"n\">objects</span><span "
            "class=\"o\">.</span><span class=\"n\">all</span><span class=\"p\">()</span>\n    "
            "<span class=\"k\">return</span> <span class=\"n\">render</span><span class=\"p\">"
            "(</span><span class=\"n\">request</span><span class=\"p\">,</span> <span class=\"s\">"
            "&#39;bands/band_listing.html&#39;</span><span class=\"p\">,</span> <span class=\"p\">"
            "{</span><span class=\"s\">&#39;bands&#39;</span><span class=\"p\">:</span> "
            "<span class=\"n\">bands</span><span class=\"p\">})</span>\n</pre></div>\n\n"
        )


class TestUtils(TestCase):
    def test_get_doc_path(self):
        # non-existent file
        self.assertEqual(get_doc_path(Path('root'), 'subpath.txt'), None)

        # existing file
        path, filename = __file__.rsplit(os.path.sep, 1)
        self.assertEqual(get_doc_path(Path(path), filename), None)
