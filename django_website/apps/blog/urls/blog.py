from django.conf.urls.defaults import *

info_dict = {
    'app_label': 'blog',
    'module_name': 'entries',
    'date_field': 'pub_date',
}

urlpatterns = patterns('django.views.generic.date_based',
   (r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\w{2})/(?P<slug>\w+)/$', 'object_detail', dict(info_dict, slug_field='slug')),
   (r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\w{2})/$', 'archive_day', info_dict),
   (r'^(?P<year>\d{4})/(?P<month>\w{3})/$', 'archive_month', info_dict),
   (r'^(?P<year>\d{4})/$', 'archive_year', info_dict),
   (r'^/?$', 'archive_index', info_dict),
)
