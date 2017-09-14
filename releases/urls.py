from django.urls import path, re_path

from .views import index, redirect

urlpatterns = [
    path('', index, name='download'),
    re_path('^([0-9a-z_.-]+)/(tarball|checksum|egg)/$', redirect, name='download-redirect'),
]
