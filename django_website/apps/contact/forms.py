import textwrap
from django import newforms as forms
from contact_form.forms import AkismetContactForm

attrs = {'class': 'required'}

class BaseContactForm(AkismetContactForm):
    message_subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs=attrs), label=u'Message subject')

    def subject(self):
        return "[Contact form] " + self.cleaned_data["message_subject"]

    def message(self):
        body = "\n".join(textwrap.wrap(self.cleaned_data["body"], 76))
        return "From: %s <%s>\n\n%s" % (self.cleaned_data["name"], self.cleaned_data["email"], body)

class FoundationContactForm(BaseContactForm):
    recipient_list = ["dsf-board@googlegroups.com"]