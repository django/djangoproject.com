"""
Legacy URLs for documentation pages.
"""

from __future__ import absolute_import

from django.conf.urls import patterns

from .views import gone

urlpatterns = patterns('',
    (r'^comments/', gone),
    (r'^rss/comments/$', gone),
    (r'^documentation', gone),
)
