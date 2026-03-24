from dataclasses import dataclass

from django.contrib import sitemaps
from django_hosts.resolvers import reverse


@dataclass
class URLObject:
    name: str
    host: str = "www"


class LocationAbsoluteUrlMixin:
    def get_urls(self, site=None, **kwargs):
        """
        Prevent the Django sitemap framework from prefixing the domain.
        Use the absolute URL returned by location().
        """
        urls = []
        for item in self.items():
            loc = self.location(item)
            urls.append(
                {
                    "location": loc,
                    "lastmod": None,
                    "changefreq": self.changefreq,
                    "priority": self.priority,
                }
            )
        return urls


class TemplateViewSitemap(LocationAbsoluteUrlMixin, sitemaps.Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return [
            # accounts
            URLObject("registration_register"),
            # aggregator
            URLObject("community-index"),
            URLObject("community-ecosystem"),
            URLObject("local-django-communities"),
            # contact
            URLObject("contact_foundation"),
            # dashboard
            URLObject("dashboard-index", host="dashboard"),
            URLObject("metric-list", host="dashboard"),
            # djangoproject
            URLObject("homepage"),
            URLObject("overview"),
            URLObject("start"),
            URLObject("code_of_conduct"),
            URLObject("conduct_faq"),
            URLObject("conduct_reporting"),
            URLObject("conduct_enforcement"),
            URLObject("conduct_changes"),
            URLObject("diversity"),
            URLObject("diversity_changes"),
            # foundation
            URLObject("foundation_meeting_archive_index"),
            # fundraising
            URLObject("fundraising:index"),
            # members
            URLObject("members:individual-members"),
            URLObject("members:corporate-members"),
            URLObject("members:corporate-members-join"),
            URLObject("members:corporate-members-badges"),
            URLObject("members:teams"),
            # releases
            URLObject("download"),
        ]

    def location(self, item):
        return reverse(item.name, host=item.host)
