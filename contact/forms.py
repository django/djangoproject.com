import logging

from django import forms
from django_contact_form.forms import AkismetContactForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

logger = logging.getLogger(__name__)


class BaseContactForm(AkismetContactForm):
    message_subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "required", "placeholder": "Message subject"}
        ),
        label="Message subject",
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"class": "required", "placeholder": "E-mail"})
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "required", "placeholder": "Name"})
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "required", "placeholder": "Your message"}
        )
    )
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def subject(self):
        # Strip all linebreaks from the subject string.
        subject = "".join(self.cleaned_data["message_subject"].splitlines())
        return "[Contact form] " + subject

    def message(self):
        return "From: {name} <{email}>\n\n{body}".format(**self.cleaned_data)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)


class FoundationContactForm(BaseContactForm):
    recipient_list = ["dsf-board@googlegroups.com"]
