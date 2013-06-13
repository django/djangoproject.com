import haystack.forms
from django import forms
from .models import DocumentRelease


class DocSearchForm(haystack.forms.SearchForm):

    def __init__(self, data=None, **kwargs):
        if data and 'release' in data:
            self.initial_rel = DocumentRelease.objects.get(pk=data['release'])
        else:
            self.initial_rel = kwargs.pop('release', DocumentRelease.objects.current())
        super(DocSearchForm, self).__init__(data=data, **kwargs)
        self.fields['q'].widget = SearchInput()
        self.fields['release'] = DocumentReleaseChoiceField(
            queryset = DocumentRelease.objects.filter(lang=self.initial_rel.lang).order_by('version'),
            initial = self.initial_rel,
            empty_label = None,
            required = False,
        )

    def search(self):
        sqs = super(DocSearchForm, self).search()
        if self.is_valid():
            rel = self.cleaned_data['release'] or DocumentRelease.objects.current()
            sqs = sqs.filter(lang=rel.lang, version=rel.version)
        return sqs

class DocumentReleaseChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.human_version

class SearchInput(forms.TextInput):
    input_type = 'search'
