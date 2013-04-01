from django.contrib import messages

from django.core import urlresolvers
from django.http import HttpResponseRedirect
from contact_form.views import contact_form
from .forms import FoundationContactForm, CoCFeedbackForm

def contact_foundation(request):
    return contact_form(request,
        form_class = FoundationContactForm,
        template_name = 'contact/foundation.html',
        success_url = urlresolvers.reverse('contact_form_sent'))

def contact_coc(request):
    resp = contact_form(request,
        form_class = CoCFeedbackForm,
        template_name = 'contact/coc.html',
        success_url = urlresolvers.reverse('code_of_conduct'))
    if isinstance(resp, HttpResponseRedirect):
        messages.success(request, "Thanks for your feedback! If you provided an email address, we'll get back to you shortly.")
    return resp
