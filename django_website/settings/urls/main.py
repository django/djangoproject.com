from django.conf.urls.defaults import *

comments_info_dict = {
    'app_label': 'comments',
    'module_name': 'freecomments',
    'paginate_by': 15,
}

aggregator_info_dict = {
    'app_label' : 'aggregator',
    'module_name' : 'feeditems',
    'paginate_by' : 15,
    'extra_lookup_kwargs': {'select_related' : True},
}

urlpatterns = patterns('',
    (r'^weblog/', include('django_website.apps.blog.urls.blog')),
    (r'^documentation/', include('django_website.apps.docs.urls.docs')),
    (r'^comments/$', 'django.views.generic.list_detail.object_list', comments_info_dict),
    (r'^comments/', include('django.contrib.comments.urls.comments')),
    (r'^community/$', 'django.views.generic.list_detail.object_list', aggregator_info_dict),
    (r'^rss/', include('django.conf.urls.rss')),
    (r'', include('django.contrib.flatpages.urls')),
)
