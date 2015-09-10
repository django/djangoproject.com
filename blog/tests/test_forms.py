from django.test import TestCase
from django.utils.timezone import now

from blog.forms import EntryForm


class EntryFormTests(TestCase):
    def generate_data(self, rst):
        return {
            'headline': 'TestEntry',
            'slug': 'testentry',
            'content_format': 'reST',
            'summary': rst,
            'body': rst,
            'pub_date': now(),
            'author': 'Django developer',
        }

    def test_validation_of_rst_errors(self):
        form = EntryForm(self.generate_data('.. tag::'))
        self.assertFalse(form.is_valid())
        self.assertIn('summary', form.errors)
        self.assertEqual(
            form.errors['summary'][0],
            'reStructuredText error at line 1: Unknown directive type &quot;tag&quot;.'
        )
        self.assertIn('body', form.errors)
        self.assertEqual(
            form.errors['body'][0],
            'reStructuredText error at line 1: Unknown directive type &quot;tag&quot;.'
        )

    def test_validation_of_rst_warnings(self):
        form = EntryForm(self.generate_data('Heading\n===='))
        form.is_valid()
        self.assertFalse(form.is_valid())
        self.assertIn('summary', form.errors)
        self.assertEqual(
            form.errors['summary'][0],
            'reStructuredText warning at line 2: Title underline too short.'
        )
        self.assertIn('body', form.errors)
        self.assertEqual(
            form.errors['body'][0],
            'reStructuredText warning at line 2: Title underline too short.'
        )
