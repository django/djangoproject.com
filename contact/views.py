from django.core import urlresolvers
from contact_form.views import ContactFormView
from .forms import FoundationContactForm

class ContactFoundation(ContactFormView):
    form_class = FoundationContactForm
    template_name = 'contact/foundation.html'

    def get_success_url(self):
        return urlresolvers.reverse('contact_form_sent')
