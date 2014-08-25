"""
Legacy URLs for documentation pages.
"""
from django.conf.urls import url

from .views import gone


urlpatterns = [
    url(r'^comments/', gone),
    url(r'^rss/comments/$', gone),
    url(r'^documentation', gone),
]
