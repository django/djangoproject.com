"""
Legacy URLs for documentation pages.
"""

from __future__ import absolute_import

from django.conf.urls import patterns

from .views import gone

urlpatterns = patterns('',
    (r'^documentation/models/$',                                      gone),
    (r'^documentation/models/(?P<slug>\w+)/$',                        gone),
    (r'^documentation/(?P<version>[\d.]+)/models/$',                  gone),
    (r'^documentation/(?P<version>[\d.]+)/models/(?P<slug>\w+)/$',    gone),
)
