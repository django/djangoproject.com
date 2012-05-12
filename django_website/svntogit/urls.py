"""
Legacy URLs for changesets.
"""

from __future__ import absolute_import

from django.conf.urls.defaults import *
from .views import redirect_to_github

urlpatterns = patterns('',
    (r'^(\d+)/?$', redirect_to_github),
)
