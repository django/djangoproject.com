"""
URLs for the profile pages (under ~)
"""

from __future__ import absolute_import
from django.conf.urls.defaults import patterns, url, include
from . import views as account_views

urlpatterns = patterns('', 
    r'^(?P<username>[\w-]+)/$', account_views.user_profile, name='user_profile'),
)
