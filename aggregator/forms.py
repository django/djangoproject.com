from django import forms

from .models import Feed


class FeedModelForm(forms.ModelForm):
    title = forms.CharField(max_length=250,
                            help_text="title of the resource / blog.")
    feed_url = forms.URLField(label='Feed URL',
                              help_text="link to the RSS/Atom feed. Please only use Django-specific feeds.")
    public_url = forms.URLField(label='Public URL',
                                help_text="link to main page (i.e. blog homepage)")

    class Meta:
        model = Feed
        exclude = ('feed_type', 'owner', 'approval_status')
