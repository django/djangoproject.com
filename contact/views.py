from django.urls import reverse
from django_contact_form.views import ContactFormView

from fundraising.sponsor_programs import (
    ASSURANCE_LEVELS,
    BANNER_LEVELS,
    MARKETING_STATS,
    SPONSORSHIP_AMOUNTS,
)

from .forms import BannerSponsorshipForm, FoundationContactForm


class ContactFoundation(ContactFormView):
    form_class = FoundationContactForm
    template_name = "contact/foundation.html"

    def get_success_url(self):
        return reverse("contact_form_sent")


class BannerSponsorship(ContactFoundation):
    form_class = BannerSponsorshipForm
    template_name = "sponsor/banner.html"
    extra_context = {"levels": BANNER_LEVELS, "stats": MARKETING_STATS}

    def get_initial(self):
        """
        Pre-select the sponsorship level named by the ``level`` query
        parameter, so the buttons on the page select the matching radio
        button. An unknown value falls back to the default of the field.
        """
        initial = super().get_initial()
        level = self.request.GET.get("level")
        if level in SPONSORSHIP_AMOUNTS:
            initial["message_subject"] = level
        return initial


class AssuranceSponsorship(ContactFoundation):
    template_name = "sponsor/assurance.html"
    extra_context = {"levels": ASSURANCE_LEVELS}

    def get_initial(self):
        initial = super().get_initial()
        level = next(
            (
                level
                for level in ASSURANCE_LEVELS
                if level["slug"] == self.request.GET.get("level")
            ),
            None,
        )
        initial["message_subject"] = (
            f"Django {level['name']} pilot" if level else "Django Assurance pilot"
        )
        return initial
