from django import forms
from django_countries import countries
from django_countries.widgets import CountrySelectWidget

from .models import Feed, LocalDjangoCommunity


class FeedModelForm(forms.ModelForm):
    title = forms.CharField(
        max_length=250,
        widget=forms.TextInput(
            attrs={
                "class": "required",
                "placeholder": "Title of the resource / blog",
            }
        ),
    )
    feed_url = forms.URLField(
        label="Feed URL",
        widget=forms.TextInput(
            attrs={
                "class": "required",
                "placeholder": (
                    "Link to the RSS/Atom feed. Please only use "
                    "Django-specific feeds."
                ),
            }
        ),
    )
    public_url = forms.URLField(
        label="Public URL",
        widget=forms.TextInput(
            attrs={
                "class": "required",
                "placeholder": "Link to main page (i.e. blog homepage)",
            }
        ),
    )

    class Meta:
        model = Feed
        exclude = ("feed_type", "owner", "approval_status")

    def clean_feed_url(self):
        feed_url = self.cleaned_data.get("feed_url")
        if feed_url and "//stackoverflow.com" in feed_url:
            raise forms.ValidationError(
                "Stack Overflow questions tagged with 'django' will appear "
                "here automatically."
            )
        return feed_url


class LocalDjangoCommunityModelForm(forms.ModelForm):
    name = forms.CharField(
        max_length=250,
        widget=forms.TextInput(
            attrs={
                "class": "required",
                "placeholder": "Name of the community",
            }
        ),
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "required",
                "placeholder": "Description of the community",
            }
        ),
    )
    continent = forms.CharField(
        max_length=250,
        widget=forms.TextInput(
            attrs={
                "class": "required",
                "placeholder": "Continent",
            }
        ),
    )
    country = forms.ChoiceField(
        widget=CountrySelectWidget(
            attrs={
                "class": "required",
                "placeholder": "Country",
            }
        ),
        choices=countries,
    )
    city = forms.CharField(
        max_length=250,
        widget=forms.TextInput(
            attrs={
                "class": "required",
                "placeholder": "City",
            }
        ),
    )
    website_url = forms.URLField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Link to the community's website",
            }
        ),
    )
    event_site_url = forms.URLField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Link to the community's event site",
            }
        ),
    )

    class Meta:
        model = LocalDjangoCommunity
        fields = (
            "name",
            "description",
            "continent",
            "country",
            "city",
            "website_url",
            "event_site_url",
        )

    def clean_feed_url(self):
        feed_url = self.cleaned_data.get("feed_url")
        if feed_url and "//stackoverflow.com" in feed_url:
            raise forms.ValidationError(
                "Stack Overflow questions tagged with 'django' will appear "
                "here automatically."
            )
        return feed_url
