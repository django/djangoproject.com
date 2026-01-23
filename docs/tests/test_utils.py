import os
from pathlib import Path

from django.test import SimpleTestCase

from ..utils import extract_inner_html, get_doc_path, sanitize_for_trigram


class TestUtils(SimpleTestCase):
    def test_get_doc_path(self):
        # non-existent file
        self.assertEqual(get_doc_path(Path("root"), "subpath.txt"), None)

        # existing file
        path, filename = __file__.rsplit(os.path.sep, 1)
        self.assertEqual(get_doc_path(Path(path), filename), None)

    def test_sanitize_for_trigram(self):
        for query, sanitized_query in [
            ("simple search", "simple search"),
            ("Python Django -Flask", "Python Django"),
            ('Python "Django Framework" -Flask', "Python Django Framework"),
            ("Développement -'Framework Django' web", "Developpement web"),
            (
                "Γλώσσα προγραμματισμού Python -'Flask και Django'",
                "Γλωσσα προγραμματισμου Python",
            ),
            (
                "Pemrograman Python -'Flask dan Django' backend",
                "Pemrograman Python backend",
            ),
            (
                "Programmazione 'Python e Django' -Flask",
                "Programmazione Python e Django",
            ),
            ("Linguagem Python -'Django e Flask' web", "Linguagem Python web"),
            ("Desarrollo Python -'Django y Flask' rápido", "Desarrollo Python rapido"),
        ]:
            with self.subTest(query=query):
                self.assertEqual(sanitize_for_trigram(query), sanitized_query)

    def test_extract_inner_html(self):
        for html, expected_output in [
            ("<main><p>Hello</p></main>", "<p>Hello</p>"),
            (
                '<header>Test</header><main id="app" class="container">'
                "<h1>Title</h1></main>",
                "<h1>Title</h1>",
            ),
            ("<main>&amp; &lt; &gt; &#169;</main>", "& < > ©"),
            ("<main></main>", ""),
            ("<main>Hello world</main>", "Hello world"),
            ("<main><h1>Hi</h1>Text<p>Bye</p></main>", "<h1>Hi</h1>Text<p>Bye</p>"),
        ]:
            with self.subTest(html=html):
                self.assertEqual(extract_inner_html(html, tag="main"), expected_output)

    def test_extract_inner_html_multiple_same_tags_raises(self):
        with self.assertRaisesMessage(
            ValueError, "<main> occurs more than once in HTML."
        ):
            extract_inner_html(
                "<main>One main</main><main id='dupe'>Two main</main>", tag="main"
            )

    def test_extract_inner_html_multiple_same_tags_nested_raises(self):
        with self.assertRaisesMessage(
            ValueError, "Nested <main> tags are not allowed."
        ):
            extract_inner_html(
                "<main>One main<main id='dupe'>Two main</main></main>", tag="main"
            )

    def test_extract_inner_html_tag_not_found_raises(self):
        with self.assertRaisesMessage(ValueError, "<main> not found in HTML."):
            extract_inner_html("<p>Test</p>", tag="main")
