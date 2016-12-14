import stripe
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class FundraisingConfig(AppConfig):
    name = 'fundraising'
    verbose_name = _("Fundraising")

    def ready(self):
        super().ready()
        stripe.api_key = settings.STRIPE_SECRET_KEY
