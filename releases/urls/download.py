from django.urls import re_path

from ..views import redirect, roadmap

urlpatterns = [
    re_path(
        "^([0-9a-z_.-]+)/(tarball|wheel|checksum)/$", redirect, name="download-redirect"
    ),
    re_path(
        r"^(?P<series>(?:\d{1,2}\.[0-2]|\d{4}))/roadmap/$", roadmap, name="roadmap"
    ),
]
