import haystack.forms
from django import forms
from .models import DocumentRelease

class DocSearchForm(haystack.forms.SearchForm):

    def __init__(self, *args, **kwargs):
        super(DocSearchForm, self).__init__(*args, **kwargs)
        self.fields['release'] = forms.ModelChoiceField(
            queryset = DocumentRelease.objects.all(),
            initial = DocumentRelease.objects.default(),
            empty_label = None,
            widget = forms.RadioSelect,
        )

    def search(self):
        sqs = super(DocSearchForm, self).search()
        rel = self.cleaned_data['release']
        return sqs.filter(lang=rel.lang, version=rel.version)

