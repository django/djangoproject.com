from django import forms
from django.utils.translation import gettext_lazy as _

search_placeholder = _('Search %s documentation')


class DocSearchForm(forms.Form):
    q = forms.CharField(required=False, label=_('Search'))

    def __init__(self, data=None, **kwargs):
        self.release = kwargs.pop('release')
        super().__init__(data=data, **kwargs)
        self.fields['q'].widget = forms.TextInput(attrs={
            'type': 'search',
            'placeholder': search_placeholder % self.release.human_version
        })
