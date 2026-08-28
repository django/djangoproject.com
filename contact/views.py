from django.urls import reverse
from django_contact_form.views import ContactFormView

from .forms import SPONSORSHIP_AMOUNTS, BannerSponsorshipForm, FoundationContactForm


class ContactFoundation(ContactFormView):
    form_class = FoundationContactForm
    template_name = "contact/foundation.html"

    def get_success_url(self):
        return reverse("contact_form_sent")


class BannerSponsorship(ContactFoundation):
    form_class = BannerSponsorshipForm
    template_name = "sponsor/banner.html"
    extra_context = {"amounts": SPONSORSHIP_AMOUNTS}
