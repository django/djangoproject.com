# Choosing a non-standard name to avoid these translations with makemessages
from django.utils.translation import gettext_lazy as gtl

from django_countries import Countries


class FantasyCountries(Countries):
    only = ["NZ", ("NV", "Neverland")]


class TranslationFallbackCountries(Countries):
    COMMON_NAMES = {"NZ": gtl("Middle Earth")}
    OLD_NAMES = {"NZ": [gtl("Middle Earth")]}


class GBRegionCountries(Countries):
    override = {
        "GB": None,
        "GB-ENG": gtl("England"),
        "GB-NIR": gtl("Northern Ireland"),
        "GB-SCT": gtl("Scotland"),
        "GB-WLS": gtl("Wales"),
    }
