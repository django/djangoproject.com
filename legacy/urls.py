"""
Legacy URLs for documentation pages.
"""
from functools import partial

from django.urls import path
from django.views import defaults

from .views import gone

urlpatterns = [
    path('comments/', gone),
    path('rss/comments/', gone),
    path('documentation', gone),

    path('400/', partial(defaults.bad_request, exception=None)),
    path('403/', partial(defaults.permission_denied, exception=None)),
    path('404/', partial(defaults.page_not_found, exception=None)),
    path('410/', gone),
    path('500/', defaults.server_error),
]
