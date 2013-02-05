from __future__ import absolute_import

from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('',
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\w-]+)/$', views.entry_detail),
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', views.archive_day),
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', views.archive_month),
   (r'^(?P<year>\d{4})/$', views.archive_year),
   url(r'^/?$', views.archive_index, name="blog-index"),
)
