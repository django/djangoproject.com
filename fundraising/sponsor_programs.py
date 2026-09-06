"""Sponsorship program copy and sourced snapshots (refs #2816 and #2817).

Amounts are proposal values. Admin-editable pricing remains tracked in #2815.
Stats are snapshots, not live traffic or promised advertising impressions.
"""

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
        "label": "website hits per month",
        "source": "DSF prospectus",
        "date": "June 2026",
        "url": "https://www.djangoproject.com/sponsor/#dsf-social-media-reach",
    },
    {
        "value": "35%",
        "label": "of surveyed Python developers use Django",
        "source": "Python Developers Survey",
        "date": "2024",
        "url": "https://lp.jetbrains.com/python-developers-survey-2024/",
    },
    {
        "value": "49.7M",
        "label": "PyPI downloads in the last month (rounded)",
        "source": "PyPI Stats",
        "date": "September 4, 2026",
        "url": "https://pypistats.org/packages/django",
    },
    {
        "value": "89.9k",
        "label": "stars on GitHub",
        "source": "django/django",
        "date": "September 4, 2026",
        "url": "https://github.com/django/django",
    },
]

ASSURANCE_LEVELS = [
    {
        "slug": "assurance",
        "name": "Assurance",
        "amount": 10000,
        "blurb": "For teams that need a formal commitment on file.",
        "benefits": [
            "A proposed signed agreement covering Django’s published "
            "release and security policy for supported versions.",
            "Annual invoicing and renewal, with multi-year commitments to discuss.",
        ],
    },
    {
        "slug": "assurance-plus",
        "name": "Assurance Plus",
        "amount": 25000,
        "blurb": "For organizations looking for a closer relationship with "
        "the Foundation.",
        "benefits": [
            "The proposed assurance agreement and annual invoicing.",
            "A listing as a supporter of the Django Software Foundation.",
            "A yearly meeting with the DSF Board.",
        ],
    },
]
