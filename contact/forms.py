from django import forms
from contact_form.forms import AkismetContactForm

attrs = {'class': 'required'}

class BaseContactForm(AkismetContactForm):
    message_subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs=attrs), label=u'Message subject')

    def subject(self):
        return "[Contact form] " + self.cleaned_data["message_subject"]

    def message(self):
        return "From: %(name)s <%(email)s>\n\n%(body)s" % self.cleaned_data

class FoundationContactForm(BaseContactForm):
    recipient_list = ["dsf-board@googlegroups.com"]
