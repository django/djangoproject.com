"""
Legacy URLs for documentation pages.
"""

from __future__ import absolute_import

from django.conf.urls.defaults import *
from .views import gone

urlpatterns = patterns('',
    (r'^$',                                             gone),
    (r'^(?P<version>[\d.]+)/$',                         gone),
    (r'^models/$',                                      gone),
    (r'^models/(?P<slug>\w+)/$',                        gone),
    (r'^(?P<version>[\d.]+)/models/$',                  gone),
    (r'^(?P<version>[\d.]+)/models/(?P<slug>\w+)/$',    gone),
    (r'^(?P<version>[\d.]+)/(?P<slug>[\w\.-]+)/$',      gone),
)
