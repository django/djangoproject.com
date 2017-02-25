from django.test import SimpleTestCase
from django.utils.safestring import SafeData

from .templatetags.markdown import markdownify


class MarkdownifyTests(SimpleTestCase):
    def test_str(self):
        result = markdownify('Line\n\n[Link](https://www.djangoproject.com)')
        self.assertEqual(
            result,
            '<p>Line</p>\n<p><a href="https://www.djangoproject.com">Link</a></p>',
        )
        self.assertIsInstance(result, SafeData)
