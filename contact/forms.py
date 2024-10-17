import logging

import django
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django_contact_form.forms import ContactForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3
from pykismet3 import Akismet, AkismetServerError

logger = logging.getLogger(__name__)


class BaseContactForm(ContactForm):
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

    def clean_body(self):
        """
        Check spam against Akismet.

        Backported from django-contact-form pre-1.0; 1.0 dropped built-in
        Akismet support.
        """
        if "body" in self.cleaned_data and getattr(settings, "AKISMET_API_KEY", None):
            try:
                akismet_api = Akismet(
                    api_key=settings.AKISMET_API_KEY,
                    blog_url="http://%s/" % Site.objects.get_current().domain,
                    user_agent="Django {}.{}.{}".format(*django.VERSION),
                )

                akismet_data = {
                    "user_ip": self.request.META.get("REMOTE_ADDR", ""),
                    "user_agent": self.request.headers.get("user-agent", ""),
                    "referrer": self.request.headers.get("referer", ""),
                    "comment_content": force_bytes(self.cleaned_data["body"]),
                    "comment_author": self.cleaned_data.get("name", ""),
                    "comment_author_email": self.cleaned_data.get("email", ""),
                    "comment_type": "contact-form",
                }
                if getattr(settings, "AKISMET_TESTING", None):
                    # Adding test argument to the request in order to
                    # tell akismet that they should ignore the request
                    # so that test runs affect the heuristics
                    akismet_data["test"] = 1
                if akismet_api.check(akismet_data):
                    raise forms.ValidationError("Akismet thinks this message is spam")
            except AkismetServerError:
                logger.error("Akismet server error")
        return self.cleaned_data["body"]


class FoundationContactForm(BaseContactForm):
    recipient_list = ["dsf-board@googlegroups.com"]
