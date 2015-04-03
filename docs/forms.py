from django import forms
from django.utils.translation import ugettext_lazy as _

search_placeholder = _('Search %s documentation')


class DocSearchForm(forms.Form):
    q = forms.CharField(required=False, label=_('Search'))

    def __init__(self, data=None, **kwargs):
        self.release = kwargs.pop('release')
        super(DocSearchForm, self).__init__(data=data, **kwargs)
        self.fields['q'].widget = forms.TextInput(attrs={
            'type': 'search',
            'placeholder': search_placeholder % self.release.human_version
        })
