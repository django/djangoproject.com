import haystack.forms
from django import forms
from .models import DocumentRelease

# Right now this just does version because we don't really have
# multiple languages. If we get them, we'll need to deal with that.

class DocSearchForm(haystack.forms.SearchForm):

    def __init__(self, version, *args, **kwargs):
        super(DocSearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget = SearchInput()
        try:
            rel = DocumentRelease.objects.get(version=version)
        except DocumentRelease.DoesNotExist:
            rel = DocumentRelease.objects.default()
        self.fields['release'] = DocumentReleaseChoiceField(
            queryset = DocumentRelease.objects.all().order_by('version'),
            initial = rel,
            empty_label = None,
            required = False,
        )

    def search(self):
        sqs = super(DocSearchForm, self).search()
        if self.is_valid():
            rel = self.cleaned_data['release'] or DocumentRelease.objects.default()
            sqs = sqs.filter(lang=rel.lang, version=rel.version)
        return sqs

class DocumentReleaseChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.human_version

class SearchInput(forms.TextInput):
    input_type = 'search'
