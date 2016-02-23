"""
Legacy URLs for documentation pages.
"""
from functools import partial

from django.conf.urls import url
from django.views import defaults

from .views import gone

urlpatterns = [
    url(r'^comments/', gone),
    url(r'^rss/comments/$', gone),
    url(r'^documentation', gone),

    url(r'^400/$', partial(defaults.bad_request, exception=None)),
    url(r'^403/$', partial(defaults.permission_denied, exception=None)),
    url(r'^404/$', partial(defaults.page_not_found, exception=None)),
    url(r'^410/$', gone),
    url(r'^500/$', defaults.server_error),
]
