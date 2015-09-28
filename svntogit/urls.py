"""
Legacy URLs for changesets.
"""
from django.conf.urls import url

from .views import redirect_to_github

urlpatterns = [
    url(r'^(\d+)/$', redirect_to_github),
]
