from django.conf.urls import url

from .views import index, redirect

urlpatterns = [
    url(r'^$', index, name='download'),
    url(r'^([0-9a-z_.-]+)/(tarball|checksum|egg)/$', redirect, name='download-redirect'),
]
