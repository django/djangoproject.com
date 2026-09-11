from django.urls import reverse
from django_contact_form.views import ContactFormView

from fundraising.models import MARKETING_STATS, SPONSORSHIP_LEVELS

from .forms import BannerSponsorshipForm, FoundationContactForm


class ContactFoundation(ContactFormView):
    form_class = FoundationContactForm
    template_name = "contact/foundation.html"

    def get_success_url(self):
        return reverse("contact_form_sent")


class BannerSponsorship(ContactFoundation):
    form_class = BannerSponsorshipForm
    template_name = "sponsor/banner.html"
    extra_context = {
        "levels": SPONSORSHIP_LEVELS,
        "stats": MARKETING_STATS,
        "stat_sources": list(dict.fromkeys(stat["source"] for stat in MARKETING_STATS)),
    }

    def get_initial(self):
        """
        Pre-select the sponsorship level named by the ``level`` query
        parameter, so the buttons on the page select the matching radio
        button. An unknown value falls back to the default of the field.
        """
        initial = super().get_initial()
        level = self.request.GET.get("level")
        if any(level == choice["slug"] for choice in SPONSORSHIP_LEVELS):
            initial["message_subject"] = level
        return initial
