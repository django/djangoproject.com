from django import forms
from django.utils.translation import pgettext_lazy

search_label_placeholder = pgettext_lazy("Action to search the whole site", "Search")


class DocSearchForm(forms.Form):
    q = forms.CharField(required=False, label=search_label_placeholder)

    def __init__(self, data=None, **kwargs):
        self.release = kwargs.pop("release")
        super().__init__(data=data, **kwargs)
        self.fields["q"].widget = forms.TextInput(
            attrs={
                "type": "search",
                "placeholder": search_label_placeholder,
            }
        )
        q_with_prefix = super().add_prefix("q")
        self.fields["q"].widget.attrs["id"] = f"id_{q_with_prefix}"

    def add_prefix(self, field_name):
        return field_name
