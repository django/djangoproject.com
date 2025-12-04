from collections.abc import MutableMapping

from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.urls import include, path, re_path
from django.views import View

from docs.models import DocumentRelease
from docs.sitemaps import DocsSitemap
from docs.urls import urlpatterns as docs_urlpatterns
from docs.views import sitemap_index


class Sitemaps(MutableMapping):
    """Lazy dict to allow for later additions to DocumentRelease languages."""

    _data = {}

    def __iter__(self):
        return iter(
            DocumentRelease.objects.values_list("lang", flat=True)
            .distinct()
            .order_by("lang")
        )

    def __getitem__(self, key):
        if key not in self._data:
            if not DocumentRelease.objects.filter(lang=key).exists():
                raise KeyError
            self._data[key] = DocsSitemap(key)
        return self._data[key]

    def __len__(self):
        return len(self.keys())

    def __delitem__(key):
        raise NotImplementedError

    def __setitem__(key, value):
        raise NotImplementedError


sitemaps = Sitemaps()


class WwwRedirectView(View):
    """
    Redirect requests to the www subdomain, preserving the path.

    This is used to redirect non-documentation pages (like /foundation/ and
    /community/) that are incorrectly accessible on docs.djangoproject.com
    to their canonical location on www.djangoproject.com.
    """

    def get(self, request, *args, **kwargs):
        scheme = getattr(settings, "HOST_SCHEME", "https")
        parent_host = getattr(settings, "PARENT_HOST", "djangoproject.com")
        redirect_url = f"{scheme}://www.{parent_host}{request.path}"
        if request.META.get("QUERY_STRING"):
            redirect_url = f"{redirect_url}?{request.META['QUERY_STRING']}"
        return HttpResponsePermanentRedirect(redirect_url)


urlpatterns = (
    [
        # Redirect non-documentation pages to the www subdomain.
        # These pages should not be accessible on docs.djangoproject.com.
        # See https://github.com/django/djangoproject.com/issues/878
        re_path(r"^foundation(?:/(?P<path>.*))?$", WwwRedirectView.as_view()),
        re_path(r"^community(?:/(?P<path>.*))?$", WwwRedirectView.as_view()),
    ]
    + docs_urlpatterns
    + [
        path("sitemap.xml", sitemap_index, {"sitemaps": sitemaps}),
        path(
            "sitemap-<section>.xml",
            sitemap,
            {"sitemaps": sitemaps},
            name="document-sitemap",
        ),
        path(
            "google79eabba6bf6fd6d3.html",
            lambda req: HttpResponse(
                "google-site-verification: google79eabba6bf6fd6d3.html"
            ),
        ),
        # This just exists to make sure we can proof that the error pages work
        # under both hostnames.
        path("", include("legacy.urls")),
    ]
)
