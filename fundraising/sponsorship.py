"""Annual plan copy for the sponsorship mockup, based on the DSF prospectus.

Source: https://www.djangoproject.com/sponsor/
Prices and tier benefits verified against the live prospectus on 2026-09-05.
Editable pricing is tracked separately in issue #2815.
"""

# Count the individual detail benefits covered by the card highlights.
# A combined highlight can cover multiple benefits; the inheritance summary
# does not count as an individually displayed benefit.
PLANS = [
    {
        "slug": "fellow",
        "company_profile": "Large organizations funding core development",
        "highlighted_benefit_count": 2,
        "distinctions": [
            {
                "title": "Quarterly meetings with a Sponsored Fellow",
                "description": "Meet regularly with a Fellow to connect with the "
                "people and "
                "ongoing "
                "work your sponsorship helps support.",
            },
            {
                "title": "Recognition from Fellows, including at events",
                "description": "Fellows acknowledge your organization publicly, "
                "including "
                "at events. "
                "This adds a personal connection to the release-note and website "
                "recognition already included with Diamond.",
            },
        ],
        "includes": "Diamond",
        "name": "Sponsored Fellow",
        "price": "200,000",
        "tagline": "Invest in the people behind Django.",
        "intro": "Help grow the Fellowship program and give the people "
        "maintaining Django "
        "more time for security, reviews, and mentoring.",
        "audience": "For organizations ready to make a lasting investment in Django’s "
        "future.",
        "highlights": [
            "Quarterly meetings with a Sponsored Fellow",
            "Recognition from Fellows, including at events",
        ],
        "benefit_groups": [
            {
                "title": "Django leadership",
                "intro": "Build a relationship with the people supporting and "
                "guiding Django.",
                "items": [
                    "Quarterly meetings with a Sponsored Django Fellow.",
                    "Public acknowledgment of your sponsorship by Fellows, "
                    "including at events.",
                    "A yearly meeting with the Django Software Foundation "
                    "Board of Directors.",
                    "A yearly meeting with the Django Project Steering Council.",
                ],
            },
            {
                "title": "Website recognition",
                "intro": "Make your commitment visible to the developers and "
                "organizations who rely on Django.",
                "items": [
                    "Your logo, link, and organization description on the "
                    "DSF Corporate Members and fundraising pages.",
                    "A Corporate Member Badge to use on your website and "
                    "in your materials.",
                    "Your logo and link in the DSF annual report.",
                    "Your logo, link, and description on the Community and "
                    "About pages.",
                    "Your logo, link, and description in the Downloads, "
                    "Documentation, and News landing-page sidebars.",
                    "Special thanks in new release notes.",
                    "Your organization’s name and link in the website footer.",
                ],
            },
            {
                "title": "Social media",
                "intro": "Introduce your organization to the wider Django community.",
                "items": [
                    "An appreciation post on your chosen platforms: Mastodon, "
                    "Bluesky, X, LinkedIn, and Reddit, with text, a link, "
                    "and a picture.",
                    "Up to 10 dedicated announcement posts or reposts per "
                    "year sharing news from your organization.",
                ],
            },
            {
                "title": "Newsletter and blog",
                "intro": "Put your work in front of developers keeping up with "
                "the Django ecosystem.",
                "items": [
                    "Up to 4 custom sponsorship slots per year in the "
                    "Django News newsletter.",
                    "Shares on Django News social media accounts: "
                    "Mastodon, Bluesky, and X.",
                    "Up to 4 posts per year on the Django website blog.",
                ],
            },
            {
                "title": "Django Discord",
                "intro": "Show up as a supporter in Django’s community spaces.",
                "items": [
                    "A Corporate Sponsor role in the Django Discord.",
                    "Up to 4 prominent announcements per year in the Django Discord.",
                ],
            },
        ],
    },
    {
        "slug": "diamond",
        "company_profile": "Large organizations",
        "highlighted_benefit_count": 5,
        "distinctions": [
            {
                "title": "Yearly meetings with Django leadership",
                "description": "Meet annually with both the Django Software Foundation "
                "Board and the "
                "Django Project Steering Council.",
            },
            {
                "title": "Recognition in release notes and the website footer",
                "description": "Receive special thanks in new release notes, plus your "
                "organization’s name and link in the Django website footer.",
            },
            {
                "title": "Up to 4 Django News ads per year",
                "description": "Share your organization with Django News "
                "newsletter readers "
                "through "
                "up to four custom sponsorship slots each year, increased from two "
                "with Platinum.",
            },
        ],
        "includes": "Platinum",
        "name": "Diamond",
        "price": "100,000",
        "tagline": "Stand behind the framework you depend on.",
        "intro": "Support Django at scale and connect your organization with the people "
        "guiding its future.",
        "audience": "For organizations whose long-term success depends on a "
        "healthy Django "
        "ecosystem.",
        "highlights": [
            "Yearly meetings with Django leadership",
            "Recognition in release notes and the website footer",
            "Up to 4 Django News ads per year",
        ],
        "benefit_groups": [
            {
                "title": "Django leadership",
                "intro": "Build a relationship with the people supporting and "
                "guiding Django.",
                "items": [
                    "A yearly meeting with the Django Software Foundation "
                    "Board of Directors.",
                    "A yearly meeting with the Django Project Steering Council.",
                ],
            },
            {
                "title": "Website recognition",
                "intro": "Make your commitment visible to the developers and "
                "organizations who rely on Django.",
                "items": [
                    "Your logo, link, and organization description on the "
                    "DSF Corporate Members and fundraising pages.",
                    "A Corporate Member Badge to use on your website and "
                    "in your materials.",
                    "Your logo and link in the DSF annual report.",
                    "Your logo, link, and description on the Community and "
                    "About pages.",
                    "Your logo, link, and description in the Downloads, "
                    "Documentation, and News landing-page sidebars.",
                    "Special thanks in new release notes.",
                    "Your organization’s name and link in the website footer.",
                ],
            },
            {
                "title": "Social media",
                "intro": "Introduce your organization to the wider Django community.",
                "items": [
                    "An appreciation post on your chosen platforms: Mastodon, "
                    "Bluesky, X, LinkedIn, and Reddit, with text, a link, "
                    "and a picture.",
                    "Up to 10 dedicated announcement posts or reposts per "
                    "year sharing news from your organization.",
                ],
            },
            {
                "title": "Newsletter and blog",
                "intro": "Put your work in front of developers keeping up with "
                "the Django ecosystem.",
                "items": [
                    "Up to 4 custom sponsorship slots per year in the "
                    "Django News newsletter.",
                    "Shares on Django News social media accounts: "
                    "Mastodon, Bluesky, and X.",
                    "Up to 4 posts per year on the Django website blog.",
                ],
            },
            {
                "title": "Django Discord",
                "intro": "Show up as a supporter in Django’s community spaces.",
                "items": [
                    "A Corporate Sponsor role in the Django Discord.",
                    "Up to 4 prominent announcements per year in the Django Discord.",
                ],
            },
        ],
    },
    {
        "slug": "platinum",
        "company_profile": "Established companies",
        "highlighted_benefit_count": 3,
        "distinctions": [
            {
                "title": "A presence on Community and About",
                "description": "Your logo, link, and description appear on these pages "
                "without the "
                "space-permitting qualification of Gold.",
            },
            {
                "title": "More opportunities to share your work",
                "description": "Receive up to two Django News ads, two Django "
                "blog posts, "
                "and seven "
                "dedicated social posts per year.",
            },
            {
                "title": "Additional sidebar opportunities",
                "description": "Placement in the Downloads, Documentation, and News "
                "landing-page "
                "sidebars is included where space permits.",
            },
        ],
        "includes": "Gold",
        "name": "Platinum",
        "price": "30,000",
        "tagline": "Django runs your business.",
        "intro": "Give back to the framework your team relies on while introducing your "
        "organization to the Django community.",
        "audience": "For established teams looking for sustained visibility and "
        "meaningful "
        "support for Django.",
        "highlights": [
            "Your logo on Community and About pages",
            "Up to 2 Django News ads per year",
            "Up to 7 social media posts per year",
        ],
        "benefit_groups": [
            {
                "title": "Website recognition",
                "intro": "Make your commitment visible to the developers and "
                "organizations who rely on Django.",
                "items": [
                    "Your logo, link, and organization description on the "
                    "DSF Corporate Members and fundraising pages.",
                    "A Corporate Member Badge to use on your website and "
                    "in your materials.",
                    "Your logo and link in the DSF annual report.",
                    "Your logo, link, and description on the Community and "
                    "About pages.",
                    "Your logo, link, and description in the Downloads, "
                    "Documentation, and News landing-page sidebars, space "
                    "permitting.",
                ],
            },
            {
                "title": "Social media",
                "intro": "Introduce your organization to the wider Django community.",
                "items": [
                    "An appreciation post on your chosen platforms: Mastodon, "
                    "Bluesky, X, LinkedIn, and Reddit, with text, a link, "
                    "and a picture.",
                    "Up to 7 dedicated announcement posts or reposts per "
                    "year sharing news from your organization.",
                ],
            },
            {
                "title": "Newsletter and blog",
                "intro": "Put your work in front of developers keeping up with "
                "the Django ecosystem.",
                "items": [
                    "Up to 2 custom sponsorship slots per year in the "
                    "Django News newsletter.",
                    "Shares on Django News social media accounts: "
                    "Mastodon, Bluesky, and X.",
                    "Up to 2 posts per year on the Django website blog.",
                ],
            },
            {
                "title": "Django Discord",
                "intro": "Show up as a supporter in Django’s community spaces.",
                "items": [
                    "A Corporate Sponsor role in the Django Discord.",
                    "Up to 3 prominent announcements per year in the Django Discord.",
                ],
            },
        ],
    },
    {
        "slug": "gold",
        "company_profile": "Growing product companies",
        "highlighted_benefit_count": 3,
        "distinctions": [
            {
                "title": "Reach Django News readers",
                "description": "Gold introduces a custom Django News newsletter "
                "sponsorship "
                "slot, up "
                "to once per year, plus shares on its social accounts.",
            },
            {
                "title": "Tell your story on the Django blog",
                "description": "Receive up to one Django website blog post per year, "
                "alongside up to "
                "five dedicated social posts.",
            },
            {
                "title": "Extend your website presence",
                "description": "Your logo, link, and description can appear on Community "
                "and About "
                "pages, space permitting.",
            },
        ],
        "includes": "Silver",
        "name": "Gold",
        "price": "13,750",
        "tagline": "Django runs your product.",
        "intro": "Support the framework behind your product and share your "
        "work with fellow "
        "Django developers.",
        "audience": "For growing organizations building their products with Django.",
        "highlights": [
            "Up to 1 Django News ad per year",
            "Up to 1 Django blog post per year",
            "Community and About placement, space permitting",
        ],
        "benefit_groups": [
            {
                "title": "Website recognition",
                "intro": "Make your commitment visible to the developers and "
                "organizations who rely on Django.",
                "items": [
                    "Your logo, link, and organization description on the "
                    "DSF Corporate Members and fundraising pages.",
                    "A Corporate Member Badge to use on your website and "
                    "in your materials.",
                    "Your logo and link in the DSF annual report.",
                    "Your logo, link, and description on the Community and "
                    "About pages, space permitting.",
                ],
            },
            {
                "title": "Social media",
                "intro": "Introduce your organization to the wider Django community.",
                "items": [
                    "An appreciation post on your chosen platforms: Mastodon, "
                    "Bluesky, X, LinkedIn, and Reddit, with text, a link, "
                    "and a picture.",
                    "Up to 5 dedicated announcement posts or reposts per "
                    "year sharing news from your organization.",
                ],
            },
            {
                "title": "Newsletter and blog",
                "intro": "Put your work in front of developers keeping up with "
                "the Django ecosystem.",
                "items": [
                    "Up to 1 custom sponsorship slot per year in the "
                    "Django News newsletter.",
                    "Shares on Django News social media accounts: "
                    "Mastodon, Bluesky, and X.",
                    "Up to 1 post per year on the Django website blog.",
                ],
            },
            {
                "title": "Django Discord",
                "intro": "Show up as a supporter in Django’s community spaces.",
                "items": [
                    "A Corporate Sponsor role in the Django Discord.",
                    "Up to 2 prominent announcements per year in the Django Discord.",
                ],
            },
        ],
    },
    {
        "slug": "silver",
        "company_profile": "Small and growing companies",
        "highlighted_benefit_count": 2,
        "distinctions": [
            {
                "title": "Share news throughout the year",
                "description": "Build on Bronze recognition with up to three dedicated "
                "social "
                "announcement posts or reposts per year.",
            },
            {
                "title": "Speak to the Discord community",
                "description": "Receive up to one prominent announcement per year in the "
                "Django "
                "Discord.",
            },
            {
                "title": "Explore a blog feature",
                "description": "Discuss a potential post on the Django website blog, "
                "subject to "
                "approval.",
            },
        ],
        "includes": "Bronze",
        "name": "Silver",
        "price": "5,500",
        "tagline": "Django is part of your stack.",
        "intro": "Become a visible supporter of the open source software your "
        "developers use "
        "every day.",
        "audience": "For teams ready to build an ongoing relationship with the Django "
        "community.",
        "highlights": [
            "Up to 3 social media posts per year",
            "Up to 1 Discord announcement per year",
        ],
        "benefit_groups": [
            {
                "title": "Website recognition",
                "intro": "Make your commitment visible to the developers and "
                "organizations who rely on Django.",
                "items": [
                    "Your logo, link, and organization description on the "
                    "DSF Corporate Members and fundraising pages.",
                    "A Corporate Member Badge to use on your website and "
                    "in your materials.",
                    "Your logo and link in the DSF annual report.",
                ],
            },
            {
                "title": "Social media",
                "intro": "Introduce your organization to the wider Django community.",
                "items": [
                    "An appreciation post on your chosen platforms: Mastodon, "
                    "Bluesky, X, LinkedIn, and Reddit, with text and a "
                    "link.",
                    "Up to 3 dedicated announcement posts or reposts per "
                    "year sharing news from your organization.",
                ],
            },
            {
                "title": "Django blog",
                "intro": "Discuss an opportunity to share your organization’s story.",
                "items": [
                    "Potential posts on the Django website blog, subject to approval."
                ],
            },
            {
                "title": "Django Discord",
                "intro": "Show up as a supporter in Django’s community spaces.",
                "items": [
                    "A Corporate Sponsor role in the Django Discord.",
                    "Up to 1 prominent announcement per year in the Django Discord.",
                ],
            },
        ],
    },
    {
        "slug": "bronze",
        "company_profile": "Small businesses and teams",
        "highlighted_benefit_count": 4,
        "distinctions": [
            {
                "title": "Become a visible supporter",
                "description": "Introduce your organization with a logo, link, and "
                "description on "
                "the corporate members and fundraising pages.",
            },
            {
                "title": "Share your commitment",
                "description": "Use a Corporate Member Badge on your own website and "
                "materials, and "
                "receive recognition in the DSF annual report.",
            },
            {
                "title": "Join the sponsor community",
                "description": "Receive a social appreciation post with text and a link, "
                "and a "
                "Corporate Sponsor role in the Django Discord.",
            },
        ],
        "name": "Bronze",
        "price": "2,200",
        "tagline": "Start giving back to Django.",
        "intro": "Join the organizations helping keep Django free, "
        "maintained, and welcoming "
        "to everyone.",
        "audience": "For smaller organizations taking their first step into annual "
        "sponsorship.",
        "highlights": [
            "Corporate member listing and badge",
            "Social media appreciation post",
            "Recognition in the annual report",
        ],
        "benefit_groups": [
            {
                "title": "Website recognition",
                "intro": "Make your commitment visible to the developers and "
                "organizations who rely on Django.",
                "items": [
                    "Your logo, link, and organization description on the "
                    "DSF Corporate Members and fundraising pages.",
                    "A Corporate Member Badge to use on your website and "
                    "in your materials.",
                    "Your logo and link in the DSF annual report.",
                ],
            },
            {
                "title": "Social media",
                "intro": "Introduce your organization to the wider Django community.",
                "items": [
                    "An appreciation post on your chosen platforms: Mastodon, "
                    "Bluesky, X, LinkedIn, and Reddit, with text and a "
                    "link."
                ],
            },
            {
                "title": "Django Discord",
                "intro": "Show up as a supporter in Django’s community spaces.",
                "items": ["A Corporate Sponsor role in the Django Discord."],
            },
        ],
    },
]
