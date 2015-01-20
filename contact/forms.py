from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.encoding import force_bytes

from akismet import Akismet
from contact_form.forms import ContactForm


class BaseContactForm(ContactForm):
    message_subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'required', 'placeholder': 'Message subject'}),
        label='Message subject',
    )
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'required', 'placeholder': 'E-mail'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'required', 'placeholder': 'Name'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'required', 'placeholder': 'Your message'}))

    def subject(self):
        # Strip all linebreaks from the subject string.
        subject = ''.join(self.cleaned_data["message_subject"].splitlines())
        return "[Contact form] " + subject

    def message(self):
        return "From: {name} <{email}>\n\n{body}".format(**self.cleaned_data)

    def clean_body(self):
        """
        Check spam against Akismet.

        Backported from django-contact-form pre-1.0; 1.0 dropped built-in
        Akismet support.
        """
        if 'body' in self.cleaned_data and hasattr(settings, 'AKISMET_API_KEY') and settings.AKISMET_API_KEY:
            akismet_api = Akismet(key=settings.AKISMET_API_KEY,
                                  blog_url='http://%s/' % Site.objects.get_current().domain)
            if akismet_api.verify_key():
                akismet_data = {'comment_type': 'comment',
                                'referer': self.request.META.get('HTTP_REFERER', ''),
                                'user_ip': self.request.META.get('REMOTE_ADDR', ''),
                                'user_agent': self.request.META.get('HTTP_USER_AGENT', '')}
                comment = force_bytes(self.cleaned_data['body'])  # workaround for #21444
                if akismet_api.comment_check(comment, data=akismet_data, build_data=True):
                    raise forms.ValidationError("Akismet thinks this message is spam")
        return self.cleaned_data['body']


class FoundationContactForm(BaseContactForm):
    recipient_list = ["dsf-board@googlegroups.com"]
