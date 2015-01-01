"""
Legacy URLs for documentation pages.
"""
from django.conf.urls import url

from .views import gone


urlpatterns = [
    url(r'^comments/', gone),
    url(r'^rss/comments/$', gone),
    url(r'^documentation', gone),

    url(r'^400/$', 'django.views.defaults.bad_request'),
    url(r'^403/$', 'django.views.defaults.permission_denied'),
    url(r'^404/$', 'django.views.defaults.page_not_found'),
    url(r'^410/$', gone),
    url(r'^500/$', 'django.views.defaults.server_error'),
]
