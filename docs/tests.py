from django.test import TestCase

from .forms import DocSearchForm
from .models import DocumentRelease


class SearchFormTestCase(TestCase):
    fixtures = ['doc_test_fixtures']

    def test_unbound_form(self):
        """
        An unbound form should have the default release selected.
        """
        release = DocumentRelease.objects.get(pk=1)
        f = DocSearchForm(default_release=release)

        self.assertIn('<option value="1" selected="selected">', f['release'].as_widget())

    def test_bound_form(self):
        """
        If no release is passed to a bound form, the default release should
        be selected.
        """
        release = DocumentRelease.objects.get(pk=1)
        f = DocSearchForm({'q': 'foo'}, default_release=release)

        self.assertIn('<option value="1" selected="selected">', f['release'].as_widget())

    def test_bound_form_with_release(self):
        """
        If a release is passed to the form, it should superscede the default
        release.
        """
        release = DocumentRelease.objects.get(pk=1)
        f = DocSearchForm({'q': 'foo', 'release': 2}, default_release=release)

        self.assertIn('<option value="2" selected="selected">', f['release'].as_widget())

    def test_form_valid_without_release(self):
        """
        If no release is bound to the form, it is still valid and it yields
        the default release passed at the construction.
        """
        release = DocumentRelease.objects.get(pk=1)
        f = DocSearchForm({'q': 'foo'}, default_release=release)

        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data['release'], release)
