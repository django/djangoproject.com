"""
Legacy URLs for documentation pages.
"""
from django.conf.urls import url
from django.views import defaults

from .views import gone

urlpatterns = [
    url(r'^comments/', gone),
    url(r'^rss/comments/$', gone),
    url(r'^documentation', gone),

    url(r'^400/$', defaults.bad_request),
    url(r'^403/$', defaults.permission_denied),
    url(r'^404/$', defaults.page_not_found),
    url(r'^410/$', gone),
    url(r'^500/$', defaults.server_error),
]
