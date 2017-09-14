from contact_form.views import ContactFormView
from django.urls import reverse

from .forms import FoundationContactForm


class ContactFoundation(ContactFormView):
    form_class = FoundationContactForm
    template_name = 'contact/foundation.html'

    def get_success_url(self):
        return reverse('contact_form_sent')
