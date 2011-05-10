from __future__ import absolute_import

from django.conf.urls.defaults import *
from django.views.generic import date_based

from .models import Entry


def prepare_arguments(view):
    def wrapped(request, *args, **kwargs):
        kwargs['allow_future'] = request.user.is_staff
        kwargs['queryset'] = Entry.objects.all() if request.user.is_staff else Entry.objects.published()
        kwargs['date_field'] = 'pub_date'
        return view(request, *args, **kwargs)
    return wrapped


urlpatterns = patterns('',
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\w-]+)/$', prepare_arguments(date_based.object_detail)),
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', prepare_arguments(date_based.archive_day)),
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', prepare_arguments(date_based.archive_month)),
   (r'^(?P<year>\d{4})/$', prepare_arguments(date_based.archive_year)),
   url(r'^/?$', prepare_arguments(date_based.archive_index), name="blog-index"),
)
