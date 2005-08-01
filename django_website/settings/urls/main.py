from django.conf.urls.defaults import *

info_dict = {
    'app_label': 'comments',
    'module_name': 'freecomments',
    'paginate_by': 15,
}

urlpatterns = patterns('',
    (r'^weblog/', include('django_website.apps.blog.urls.blog')),
    (r'^documentation/', include('django_website.apps.docs.urls.docs')),
    (r'^comments/$', 'django.views.generic.list_detail.object_list', info_dict),
    (r'^comments/', include('django.contrib.comments.urls.comments')),
    (r'^rss/', include('django.conf.urls.rss')),
    (r'', include('django.conf.urls.flatfiles')),
)
