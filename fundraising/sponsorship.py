"""Annual plan copy for the sponsorship mockup, based on the DSF prospectus.

Source: the prospectus, now served at /sponsor/plans/.
Prices and tier benefits verified against the live prospectus on 2026-09-05.
Editable pricing is tracked separately in issue #2815.
"""

from django.utils.translation import gettext_lazy as _

# Count the individual detail benefits covered by the card highlights.
# A combined highlight can cover multiple benefits; the inheritance summary
# does not count as an individually displayed benefit.
PLANS = [
    {
        "slug": "fellow",
        "first_sponsor": _("Be our first Fellowship sponsor"),
        "company_profile": _("Large organizations funding core development"),
        "highlighted_benefit_count": 2,
        "includes": _("Diamond"),
        "name": _("Sponsored Fellow"),
        "price": "200,000",
        "tagline": _("Invest in the people behind Django."),
        "intro": _(
            "Help grow the Fellowship program and give the people maintaining Django "
            "more time for security, reviews, and mentoring."
        ),
        "audience": _(
            "For organizations ready to make a lasting investment in Django's future."
        ),
        "highlights": [
            _("Quarterly meetings with a Sponsored Fellow"),
            _("Recognition from Fellows, including at events"),
        ],
        "benefit_groups": [
            {
                "title": _("Django leadership"),
                "items": [
                    _("Quarterly meetings with a Sponsored Django Fellow."),
                    _(
                        "Public acknowledgment of your sponsorship by Fellows, "
                        "including at events."
                    ),
                    _(
                        "A yearly meeting with the Django Software Foundation Board of "
                        "Directors."
                    ),
                    _("A yearly meeting with the Django Project Steering Council."),
                ],
            },
            {
                "title": _("Website recognition"),
                "items": [
                    _(
                        "Your logo, link, and organization description on the DSF "
                        "Corporate Members and fundraising pages."
                    ),
                    _(
                        "A Corporate Member Badge to use on your website and in your "
                        "materials."
                    ),
                    _("Your logo and link in the DSF annual report."),
                    _(
                        "Your logo, link, and description on the Community and About "
                        "pages."
                    ),
                    _(
                        "Your logo, link, and description in the Downloads, "
                        "Documentation, and News landing-page sidebars."
                    ),
                    _("Special thanks in new release notes."),
                    _("Your organization's name and link in the website footer."),
                ],
            },
            {
                "title": _("Social media"),
                "items": [
                    _(
                        "An appreciation post on your chosen platforms: Mastodon, "
                        "Bluesky, X, LinkedIn, and Reddit, with text, a link, and a "
                        "picture."
                    ),
                    _(
                        "Up to 10 dedicated announcement posts or reposts per year "
                        "sharing news from your organization."
                    ),
                ],
            },
            {
                "title": _("Newsletter and blog"),
                "items": [
                    _(
                        "Up to 4 custom sponsorship slots per year in the Django News "
                        "newsletter."
                    ),
                    _(
                        "Shares on Django News social media accounts: Mastodon, "
                        "Bluesky, and X."
                    ),
                    _("Up to 4 posts per year on the Django website blog."),
                ],
            },
            {
                "title": _("Django Discord"),
                "items": [
                    _("A Corporate Sponsor role in the Django Discord."),
                    _(
                        "Up to 4 prominent announcements per year in the Django "
                        "Discord."
                    ),
                ],
            },
        ],
    },
    {
        "slug": "diamond",
        "first_sponsor": _("Be our first Diamond sponsor"),
        "company_profile": _("Large organizations"),
        "highlighted_benefit_count": 5,
        "includes": _("Platinum"),
        "name": _("Diamond"),
        "price": "100,000",
        "tagline": _("Stand behind the framework you depend on."),
        "intro": _(
            "Support Django at scale and connect your organization with the people "
            "guiding its future."
        ),
        "audience": _(
            "For organizations whose long-term success depends on a healthy Django "
            "ecosystem."
        ),
        "highlights": [
            _("Yearly meetings with Django leadership"),
            _("Recognition in release notes and the website footer"),
            _("Up to 4 Django News ads per year"),
        ],
        "benefit_groups": [
            {
                "title": _("Django leadership"),
                "items": [
                    _(
                        "A yearly meeting with the Django Software Foundation Board of "
                        "Directors."
                    ),
                    _("A yearly meeting with the Django Project Steering Council."),
                ],
            },
            {
                "title": _("Website recognition"),
                "items": [
                    _(
                        "Your logo, link, and organization description on the DSF "
                        "Corporate Members and fundraising pages."
                    ),
                    _(
                        "A Corporate Member Badge to use on your website and in your "
                        "materials."
                    ),
                    _("Your logo and link in the DSF annual report."),
                    _(
                        "Your logo, link, and description on the Community and About "
                        "pages."
                    ),
                    _(
                        "Your logo, link, and description in the Downloads, "
                        "Documentation, and News landing-page sidebars."
                    ),
                    _("Special thanks in new release notes."),
                    _("Your organization's name and link in the website footer."),
                ],
            },
            {
                "title": _("Social media"),
                "items": [
                    _(
                        "An appreciation post on your chosen platforms: Mastodon, "
                        "Bluesky, X, LinkedIn, and Reddit, with text, a link, and a "
                        "picture."
                    ),
                    _(
                        "Up to 10 dedicated announcement posts or reposts per year "
                        "sharing news from your organization."
                    ),
                ],
            },
            {
                "title": _("Newsletter and blog"),
                "items": [
                    _(
                        "Up to 4 custom sponsorship slots per year in the Django News "
                        "newsletter."
                    ),
                    _(
                        "Shares on Django News social media accounts: Mastodon, "
                        "Bluesky, and X."
                    ),
                    _("Up to 4 posts per year on the Django website blog."),
                ],
            },
            {
                "title": _("Django Discord"),
                "items": [
                    _("A Corporate Sponsor role in the Django Discord."),
                    _(
                        "Up to 4 prominent announcements per year in the Django "
                        "Discord."
                    ),
                ],
            },
        ],
    },
    {
        "slug": "platinum",
        "first_sponsor": _("Be our first Platinum sponsor"),
        "company_profile": _("Established companies"),
        "highlighted_benefit_count": 3,
        "includes": _("Gold"),
        "name": _("Platinum"),
        "price": "30,000",
        "tagline": _("Django runs your business."),
        "intro": _(
            "Give back to the framework your team relies on while introducing your "
            "organization to the Django community."
        ),
        "audience": _(
            "For established teams looking for sustained visibility and meaningful "
            "support for Django."
        ),
        "highlights": [
            _("Your logo on Community and About pages"),
            _("Up to 2 Django News ads per year"),
            _("Up to 7 social media posts per year"),
        ],
        "benefit_groups": [
            {
                "title": _("Website recognition"),
                "items": [
                    _(
                        "Your logo, link, and organization description on the DSF "
                        "Corporate Members and fundraising pages."
                    ),
                    _(
                        "A Corporate Member Badge to use on your website and in your "
                        "materials."
                    ),
                    _("Your logo and link in the DSF annual report."),
                    _(
                        "Your logo, link, and description on the Community and About "
                        "pages."
                    ),
                    _(
                        "Your logo, link, and description in the Downloads, "
                        "Documentation, and News landing-page sidebars, space "
                        "permitting."
                    ),
                ],
            },
            {
                "title": _("Social media"),
                "items": [
                    _(
                        "An appreciation post on your chosen platforms: Mastodon, "
                        "Bluesky, X, LinkedIn, and Reddit, with text, a link, and a "
                        "picture."
                    ),
                    _(
                        "Up to 7 dedicated announcement posts or reposts per year "
                        "sharing news from your organization."
                    ),
                ],
            },
            {
                "title": _("Newsletter and blog"),
                "items": [
                    _(
                        "Up to 2 custom sponsorship slots per year in the Django News "
                        "newsletter."
                    ),
                    _(
                        "Shares on Django News social media accounts: Mastodon, "
                        "Bluesky, and X."
                    ),
                    _("Up to 2 posts per year on the Django website blog."),
                ],
            },
            {
                "title": _("Django Discord"),
                "items": [
                    _("A Corporate Sponsor role in the Django Discord."),
                    _(
                        "Up to 3 prominent announcements per year in the Django "
                        "Discord."
                    ),
                ],
            },
        ],
    },
    {
        "slug": "gold",
        "first_sponsor": _("Be our first Gold sponsor"),
        "company_profile": _("Growing product companies"),
        "highlighted_benefit_count": 3,
        "includes": _("Silver"),
        "name": _("Gold"),
        "price": "13,750",
        "tagline": _("Django runs your product."),
        "intro": _(
            "Support the framework behind your product and share your work with fellow "
            "Django developers."
        ),
        "audience": _("For growing organizations building their products with Django."),
        "highlights": [
            _("Up to 1 Django News ad per year"),
            _("Up to 1 Django blog post per year"),
            _("Community and About placement, space permitting"),
        ],
        "benefit_groups": [
            {
                "title": _("Website recognition"),
                "items": [
                    _(
                        "Your logo, link, and organization description on the DSF "
                        "Corporate Members and fundraising pages."
                    ),
                    _(
                        "A Corporate Member Badge to use on your website and in your "
                        "materials."
                    ),
                    _("Your logo and link in the DSF annual report."),
                    _(
                        "Your logo, link, and description on the Community and About "
                        "pages, space permitting."
                    ),
                ],
            },
            {
                "title": _("Social media"),
                "items": [
                    _(
                        "An appreciation post on your chosen platforms: Mastodon, "
                        "Bluesky, X, LinkedIn, and Reddit, with text, a link, and a "
                        "picture."
                    ),
                    _(
                        "Up to 5 dedicated announcement posts or reposts per year "
                        "sharing news from your organization."
                    ),
                ],
            },
            {
                "title": _("Newsletter and blog"),
                "items": [
                    _(
                        "Up to 1 custom sponsorship slot per year in the Django News "
                        "newsletter."
                    ),
                    _(
                        "Shares on Django News social media accounts: Mastodon, "
                        "Bluesky, and X."
                    ),
                    _("Up to 1 post per year on the Django website blog."),
                ],
            },
            {
                "title": _("Django Discord"),
                "items": [
                    _("A Corporate Sponsor role in the Django Discord."),
                    _(
                        "Up to 2 prominent announcements per year in the Django "
                        "Discord."
                    ),
                ],
            },
        ],
    },
    {
        "slug": "silver",
        "first_sponsor": _("Be our first Silver sponsor"),
        "company_profile": _("Small and growing companies"),
        "highlighted_benefit_count": 2,
        "includes": _("Bronze"),
        "name": _("Silver"),
        "price": "5,500",
        "tagline": _("Django is part of your stack."),
        "intro": _(
            "Become a visible supporter of the open source software your developers "
            "use every day."
        ),
        "audience": _(
            "For teams ready to build an ongoing relationship with the Django "
            "community."
        ),
        "highlights": [
            _("Up to 3 social media posts per year"),
            _("Up to 1 Discord announcement per year"),
        ],
        "benefit_groups": [
            {
                "title": _("Website recognition"),
                "items": [
                    _(
                        "Your logo, link, and organization description on the DSF "
                        "Corporate Members and fundraising pages."
                    ),
                    _(
                        "A Corporate Member Badge to use on your website and in your "
                        "materials."
                    ),
                    _("Your logo and link in the DSF annual report."),
                ],
            },
            {
                "title": _("Social media"),
                "items": [
                    _(
                        "An appreciation post on your chosen platforms: Mastodon, "
                        "Bluesky, X, LinkedIn, and Reddit, with text and a link."
                    ),
                    _(
                        "Up to 3 dedicated announcement posts or reposts per year "
                        "sharing news from your organization."
                    ),
                ],
            },
            {
                "title": _("Django blog"),
                "items": [
                    _(
                        "Potential posts on the Django website blog, subject to "
                        "approval."
                    ),
                ],
            },
            {
                "title": _("Django Discord"),
                "items": [
                    _("A Corporate Sponsor role in the Django Discord."),
                    _("Up to 1 prominent announcement per year in the Django Discord."),
                ],
            },
        ],
    },
    {
        "slug": "bronze",
        "first_sponsor": _("Be our first Bronze sponsor"),
        "company_profile": _("Small businesses and teams"),
        "highlighted_benefit_count": 4,
        "name": _("Bronze"),
        "price": "2,200",
        "tagline": _("Start giving back to Django."),
        "intro": _(
            "Join the organizations helping keep Django free, maintained, and "
            "welcoming to everyone."
        ),
        "audience": _(
            "For smaller organizations taking their first step into annual sponsorship."
        ),
        "highlights": [
            _("Corporate member listing and badge"),
            _("Social media appreciation post"),
            _("Recognition in the annual report"),
        ],
        "benefit_groups": [
            {
                "title": _("Website recognition"),
                "items": [
                    _(
                        "Your logo, link, and organization description on the DSF "
                        "Corporate Members and fundraising pages."
                    ),
                    _(
                        "A Corporate Member Badge to use on your website and in your "
                        "materials."
                    ),
                    _("Your logo and link in the DSF annual report."),
                ],
            },
            {
                "title": _("Social media"),
                "items": [
                    _(
                        "An appreciation post on your chosen platforms: Mastodon, "
                        "Bluesky, X, LinkedIn, and Reddit, with text and a link."
                    ),
                ],
            },
            {
                "title": _("Django Discord"),
                "items": [
                    _("A Corporate Sponsor role in the Django Discord."),
                ],
            },
        ],
    },
]
