from __future__ import absolute_import, unicode_literals

from django.conf.urls import patterns, url

from .views import index, redirect

urlpatterns = patterns('',
    url(r'^$', index, name='download'),
    url(r'^([0-9a-z_.-]+)/(tarball|checksum|egg)/$', redirect, name='download-redirect'),
)
