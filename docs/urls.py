from django.conf import settings
from django.urls import path, re_path
from django.views.generic import RedirectView

from . import views, views_debug

urlpatterns = [
    path("", views.index, name="homepage"),
    path("search/", views.redirect_search),
    path("<lang>/", views.language),
    re_path(
        r"^[a-z-]+/[\w.-]+/internals/team/$",
        RedirectView.as_view(
            url="https://www.djangoproject.com/foundation/teams/",
            permanent=True,
        ),
    ),
    re_path("^(?P<lang>[a-z-]+)/(?P<version>stable)/(?P<url>.*)$", views.stable),
    re_path(
        r"^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/$",
        views.document,
        {"url": ""},
        name="document-index",
    ),
    re_path(
        r"^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_images/(?P<path>.*)$",
        views_debug.sphinx_static,
        {"subpath": "_images"},
    ),
    re_path("^(.*)/index/$", views.redirect_index),
    re_path(
        r"^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/$",
        views.search_results,
        name="document-search",
    ),
    re_path(
        r"^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/description/$",
        views.search_description,
        name="document-search-description",
    ),
    re_path(
        r"^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/suggestions/$",
        views.search_suggestions,
        name="document-search-suggestions",
    ),
    re_path(
        r"^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<url>[\w./-]*)/$",
        views.document,
        name="document-detail",
    ),
]

if settings.DEBUG:
    # Patterns for sphinx (in production they are served by nginx directly)
    # They need to be inserted at the beginning to take precedence over document-detail
    urlpatterns = [
        re_path(
            r"^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_objects/$",
            views_debug.objects_inventory,
        ),
        re_path(
            r"^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<subpath>_downloads|_source)/(?P<path>.*)$",  # noqa: E501
            views_debug.sphinx_static,
        ),
        re_path(r"^pots/(?P<pot_name>\w+\.pot)$", views_debug.pot_file),
        *urlpatterns,
    ]
