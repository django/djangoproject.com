from django.conf.urls.defaults import *

urlpatterns = patterns('django_website.apps.docs.views',
    (r'^$',                                             'doc_index'),
    (r'^(?P<version>[\d.]+)/$',                         'doc_index'),
    (r'^models/$',                                      'model_index'),
    (r'^models/(?P<slug>\w+)/$',                        'model_detail'),
    (r'^(?P<version>[\d.]+)/models/$',                  'model_index'),
    (r'^(?P<version>[\d.]+)/models/(?P<slug>\w+)/$',    'model_detail'),
    #(r'^(?P<slug>[\w\.-]+)/$',                          'doc_detail'),
    (r'^(?P<version>[\d.]+)/(?P<slug>[\w\.-]+)/$',      'doc_detail'),
)
