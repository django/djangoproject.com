from django.urls import path, re_path

from .views import index, redirect, roadmap

urlpatterns = [
    path("", index, name="download"),
    re_path(
        "^([0-9a-z_.-]+)/(tarball|wheel|checksum)/$", redirect, name="download-redirect"
    ),
    re_path(r"^(?P<series>\d{1,2}\.[0-2])/roadmap/$", roadmap, name="roadmap"),
]
