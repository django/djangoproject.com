import textwrap
from django import newforms as forms
from contact_form.forms import AkismetContactForm

attrs = {'class': 'required'}

class BaseContactForm(AkismetContactForm):
    message_subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs=attrs), label=u'Message subject')

    def subject(self):
        return "[Contact form] " + self.cleaned_data["message_subject"]

    def message(self):
        return textwrap.wrap(self.cleaned_data["body"], 76)

class FoundationContactForm(BaseContactForm):
    pass