from __future__ import absolute_import, unicode_literals

from django.conf.urls import patterns

from .views import index, redirect

urlpatterns = patterns('',
    (r'^$', index),
    (r'^([0-9a-z_.-]+)/(tarball|checksum|egg)/$', redirect),
)
