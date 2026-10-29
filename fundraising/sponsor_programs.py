"""Sponsorship program copy and sourced snapshots (refs #2803).

Amounts are proposal values. Admin-editable pricing remains tracked in #2815.
Stats are snapshots, not live traffic or promised advertising impressions.
"""

from django.urls import reverse_lazy
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

BANNER_LEVELS = [
    {
        "slug": "monthly",
        "name": _("One month"),
        "amount": 10000,
        "period": _("month"),
        "blurb": _("For brand building and hiring."),
    },
    {
        "slug": "weekly",
        "name": _("One week"),
        "amount": 3000,
        "period": _("week"),
        "blurb": _("For launches and events."),
    },
]
SPONSORSHIP_AMOUNTS = {level["slug"]: level["amount"] for level in BANNER_LEVELS}

MARKETING_STATS = [
    {
        "value": "70M+",
        "label": _("website hits per month"),
        "source": _("DSF prospectus"),
        "date": _("June 2026"),
        "url": format_lazy(
            "{}#dsf-social-media-reach", reverse_lazy("sponsor_prospectus_plans")
        ),
    },
    {
        "value": "35%",
        "label": _("of surveyed Python developers use Django"),
        "source": "Python Developers Survey",
        "date": "2024",
        "url": "https://lp.jetbrains.com/python-developers-survey-2024/",
    },
    {
        "value": "49.7M",
        "label": _("PyPI downloads in the last month (rounded)"),
        "source": "PyPI Stats",
        "date": _("September 4, 2026"),
        "url": "https://pypistats.org/packages/django",
    },
    {
        "value": "89.9k",
        "label": _("stars on GitHub"),
        "source": "django/django",
        "date": _("September 4, 2026"),
        "url": "https://github.com/django/django",
    },
]
