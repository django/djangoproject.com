import logging

import django
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django_contact_form.forms import (  # Use AkismetContactForm instead of ContactForm
    AkismetContactForm,
)
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

logger = logging.getLogger(__name__)


class BaseContactForm(AkismetContactForm):  # Inherit from AkismetContactForm
    message_subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "required", "placeholder": _("Message subject")}
        ),
        label=_("Message subject"),
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"class": "required", "placeholder": _("E-mail")})
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "required", "placeholder": _("Name")})
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "required", "placeholder": _("Your message")}
        )
    )
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def subject(self):
        # Strip all linebreaks from the subject string.
        subject = "".join(self.cleaned_data["message_subject"].splitlines())
        return "[Contact form] " + subject

    def message(self):
        return "From: {name} <{email}>\n\n{body}".format(**self.cleaned_data)

    # Remove the custom clean_body() method. The spam check is now handled by AkismetContactForm


class FoundationContactForm(BaseContactForm):
    recipient_list = ["dsf-board@googlegroups.com"]
