"""
Legacy URLs for changesets.
"""
from django.urls import path

from .views import redirect_to_github

urlpatterns = [
    path('<int:svn_revision>/', redirect_to_github),
]
