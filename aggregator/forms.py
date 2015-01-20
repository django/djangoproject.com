from django import forms

from .models import Feed


class FeedModelForm(forms.ModelForm):
    title = forms.CharField(
        max_length=250,
        widget=forms.TextInput(attrs={
            'class': 'required',
            'placeholder': 'Title of the resource / blog',
        }),
    )
    feed_url = forms.URLField(
        label='Feed URL',
        widget=forms.TextInput(attrs={
            'class': 'required',
            'placeholder': 'Link to the RSS/Atom feed. Please only use Django-specific feeds.',
        }),
    )
    public_url = forms.URLField(
        label='Public URL',
        widget=forms.TextInput(attrs={
            'class': 'required',
            'placeholder': 'Link to main page (i.e. blog homepage)',
        }),
    )

    class Meta:
        model = Feed
        exclude = ('feed_type', 'owner', 'approval_status')
