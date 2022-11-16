from django.urls import re_path

from ..views import redirect

urlpatterns = [
    re_path('^([0-9a-z_.-]+)/(tarball|checksum|egg)/$', redirect, name='download-redirect'),
]
