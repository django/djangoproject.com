import haystack.forms
from django import forms
from .models import DocumentRelease


class DocumentReleaseChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('empty_label', None)
        kwargs.setdefault('queryset', DocumentRelease.objects.order_by('version'))
        super(DocumentReleaseChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.human_version

    def bound_data(self, data, initial):
        """
        If no data is given, return the initial data.
        This allows for a default release to always be selected, even if none
        was provided in the URL.
        """
        return data or initial


class DocSearchForm(haystack.forms.SearchForm):
    release = DocumentReleaseChoiceField()

    def __init__(self, data=None, **kwargs):
        self.default_release = kwargs.pop('default_release')
        super(DocSearchForm, self).__init__(data=data, **kwargs)
        self.fields['q'].widget = forms.TextInput(attrs={'type': 'search', 'placeholder': 'Search documentation'})
        self.fields['release'].queryset = self.fields['release'].queryset.filter(lang=self.default_release.lang)
        self.fields['release'].initial = self.default_release

    def search(self):
        results = super(DocSearchForm, self).search()
        assert self.cleaned_data  # SearchForm.search() calls is_valid()
        release = self.cleaned_data['release']
        results = results.filter(lang=release.lang, version=release.version)
        return results

    def clean_release(self):
        """If no release is provided we fall back to the default release."""
        release = self.cleaned_data.get('release')
        return release if release else self.default_release
