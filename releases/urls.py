from __future__ import absolute_import, unicode_literals

from django.conf.urls import patterns

from .views import download_redirect

urlpatterns = patterns('',
    (r'^([0-9a-z_.-]+)/(tarball|checksum|egg)/$', download_redirect),
)
