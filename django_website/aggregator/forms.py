from __future__ import absolute_import

from django import forms
from django.forms import widgets
from .models import Feed, FeedType

class FeedModelForm(forms.ModelForm):
    title = forms.CharField(max_length=250, help_text="The name of the resource / blog.")
    feed_url = forms.URLField(help_text="URL to the feed.")
    public_url = forms.URLField(help_text="URL to main page of the resource (ie: blog homepage)")
    feed_type = forms.ModelChoiceField(widget=forms.widgets.HiddenInput,
                                        queryset=FeedType.objects.all())
    class Meta:
        model = Feed
        exclude = ('is_defunct',)
