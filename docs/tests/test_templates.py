import os
import shutil
import tempfile
from pathlib import Path

from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase

from releases.models import Release

from ..models import Document, DocumentRelease
from ..templatetags.docs import (
    code_links,
    generate_scroll_to_text_fragment,
    get_all_doc_versions,
)


class TemplateTagTests(TestCase):
    fixtures = ["doc_test_fixtures"]

    def test_get_all_doc_versions_empty(self):
        with self.assertNumQueries(1):
            self.assertEqual(get_all_doc_versions({}), ["dev"])

    def test_get_all_doc_versions(self):
        tmp_docs_build_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_docs_build_root)
        os.makedirs(tmp_docs_build_root.joinpath("en", "1.8", "_built", "json"))
        os.makedirs(tmp_docs_build_root.joinpath("en", "1.11", "_built", "json"))
        with self.settings(DOCS_BUILD_ROOT=tmp_docs_build_root):
            self.assertEqual(get_all_doc_versions({}), ["1.8", "1.11", "dev"])

    def test_pygments_template_tag(self):
        template = Template(
            '''
{% load docs %}
{% pygment 'python' %}
def band_listing(request):
    """A view of all bands."""
    bands = models.Band.objects.all()
    return render(request, 'bands/band_listing.html', {'bands': bands})

{% endpygment %}
'''
        )
        self.assertHTMLEqual(
            template.render(Context()),
            """
<div class="highlight"><pre>
<span></span>
<span class="k">def</span><span class="w"> </span>
<span class="nf">band_listing</span>
<span class="p">(</span><span class="n">request</span>
<span class="p">):</span>
<span class="w">    </span>
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
</pre></div>
            """,
        )

    def test_fragment_template_tag(self):
        highlighted_text = (
            "<mark>testing</mark> frameworks   section of   Advanced <mark>testing"
            "</mark> topics  .\nWriting and running <mark>tests</mark>\n<mark>"
            "Testing</mark> tools\nAdvanced <mark>testing</mark>\n<mark>tests</mark> ¶"
        )
        template = Template(
            "{% load docs %}"
            "https://docs.djangoproject.com/en/5.1/topics/testing/"
            "{{ highlighted_text|fragment }}"
        )
        self.assertHTMLEqual(
            template.render(Context({"highlighted_text": highlighted_text})),
            "https://docs.djangoproject.com/en/5.1/topics/testing/"
            "#:~:text=testing%20frameworks%20section%20of%20Advanced%20testing"
            "%20topics.",
        )

    def test_generate_scroll_to_text_fragment(self):
        stacked_inline = """"<mark>StackedInline</mark>     [source]    ¶
        The admin interface has the ability to edit models"""
        text_choices = """<mark>TextChoices</mark>  ):
         FRESHMAN   =   &quot;FR&quot;  ,   _  (  &quot;Freshman&quot;  )
         SOPHOMORE   =   &quot;SO&quot;  ,   _  (  &quot;Sophomore&quot;  )
         JUNIOR"""
        nested_text_choices = (
            "<mark>TextChoices</mark>  (  &quot;Medal&quot;  ,   &quot;GOLD "
            "SILVER BRONZE&quot;  )\n\n       SPORT_CHOICES   =   [\n(  &quot;"
            "Martial Arts&quot;  ,   [(  &quot;judo\n"
        )
        cases = [
            (
                stacked_inline,
                "#:~:text=%22StackedInline%5Bsource%5D",
            ),
            (
                text_choices,
                "#:~:text=TextChoices%29%3A",
            ),
            (
                nested_text_choices,
                "#:~:text=TextChoices%28%22Medal%22%2C%20%22GOLD%20SILVER%20"
                "BRONZE%22%29",
            ),
            (
                """<mark>TextChoices</mark>  ,   IntegerChoices  , and   Choices
                are now available as a way to define    Field.choices   .
                <mark>TextChoices</mark> and   IntegerChoices""",
                "#:~:text=TextChoices%2C%20IntegerChoices%2C%20and%20Choices",
            ),
            (
                """<mark>TextChoices</mark>   or   IntegerChoices  ) instances.
                Any Django field
                Any function or method reference (e.g.   datetime.datetime.today  )
                (must""",
                "#:~:text=TextChoices%20or%20IntegerChoices%29%20instances.",
            ),
            (
                """<mark>database</mark> configuration in    <mark>DATABASES</mark>   :

                settings.py    ¶
                <mark>DATABASES</mark>   =   {
                &quot;default&quot;  :   {
                    &quot;ENGINE&quot;  :   &quot;django.db.backends.postgresql&quot;  ,
                    &quot;OPTIONS""",
                "#:~:text=database%20configuration%20in%20DATABASES%3A",
            ),
            (
                """
                <mark>Generic</mark> <mark>views</mark> ¶
                See   Built-in class-based <mark>views</mark> API  . """,
                "#:~:text=Generic%20views",
            ),
        ]
        for text, url_text_fragment in cases:
            with self.subTest(url_text_fragment=url_text_fragment):
                self.assertEqual(
                    generate_scroll_to_text_fragment(text),
                    url_text_fragment,
                )

    def test_code_links(self):
        python_objects = {
            "Layer": "django.contrib.gis.gdal.Layer",
            "Migration.initial": "django.db.migrations.Migration.initial",
            "db_for_write": "db_for_write",
        }
        for searched_python_objects, expected in [
            (None, {}),
            ("", {}),
            ("Layer initial db_for_write", {}),
            (
                "Layer initial <mark>db_for</mark>_write",
                {"db_for_write": {"full_path": "db_for_write", "module_path": None}},
            ),
            (
                "<mark>Layer</mark> <mark>initial</mark> <mark>db_for</mark>_write",
                {
                    "db_for_write": {"full_path": "db_for_write", "module_path": None},
                    "Layer": {
                        "full_path": "django.contrib.gis.gdal.Layer",
                        "module_path": "django.contrib.gis.gdal",
                    },
                    "Migration.initial": {
                        "full_path": "django.db.migrations.Migration.initial",
                        "module_path": "django.db.migrations",
                    },
                },
            ),
        ]:
            with self.subTest(searched_python_objects=searched_python_objects):
                self.assertEqual(
                    code_links(searched_python_objects, python_objects),
                    expected,
                )


class TemplateTestCase(TestCase):
    def _assertOGTitleEqual(self, doc, expected):
        output = render_to_string(
            "docs/doc.html",
            {"doc": doc, "lang": "en", "version": "5.0"},
            request=RequestFactory().get("/"),
        )
        self.assertInHTML(f'<meta property="og:title" content="{expected}" />', output)

    def test_opengraph_title(self):
        doc = Document.objects.create(
            release=DocumentRelease.objects.create(
                lang="en",
                release=Release.objects.create(version="5.0"),
            ),
        )
        doc.body = "test body"  # avoids trying to load the underlying physical file

        for title, expected in [
            ("test title", "test title"),
            ("test & title", "test &amp; title"),
            ('test "title"', "test &quot;title&quot;"),
            ("test <strong>title</strong>", "test title"),
        ]:
            doc.title = title
            with self.subTest(title=title):
                self._assertOGTitleEqual(doc, f"{expected} | Django documentation")
