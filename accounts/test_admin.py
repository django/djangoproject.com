from django.test import TestCase
from django.utils.functional import Promise

from .admin import ProfileAdminForm


class ProfileAdminFormTests(TestCase):
    def test_bio_field_has_max_length(self):
        form = ProfileAdminForm()
        self.assertIn("bio", form.fields)
        self.assertIn("maxlength", form.fields["bio"].widget.attrs)
        self.assertIsInstance(form.fields["bio"].widget.attrs["maxlength"], int)

    def test_bio_field_has_help_text(self):
        form = ProfileAdminForm()
        self.assertIn("bio", form.fields)
        self.assertIsInstance(form.fields["bio"].help_text, (str, Promise))
        self.assertGreater(len(form.fields["bio"].help_text), 0)
