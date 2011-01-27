from __future__ import absolute_import

from django import forms
from django.forms import widgets
from .models import Feed, FeedType

class FeedModelForm(forms.ModelForm):
    title = forms.CharField(max_length=250,
                            help_text="title of the resource / blog.")
    feed_url = forms.URLField(label='Feed URL',
                              help_text="link to the RSS/Atom feed. Please only use Django-specific feeds.")
    public_url = forms.URLField(label='Public URL',
                                help_text="link to main page (i.e. blog homepage)")

    class Meta:
        model = Feed
        exclude = ('is_defunct', 'feed_type')
