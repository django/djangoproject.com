"""
URLs for the profile pages (under ~)
"""
from django.conf.urls import url

from . import views as account_views


urlpatterns = [
    url(r'^(?P<username>[\w-]+)/$', account_views.user_profile, name='user_profile'),
]
