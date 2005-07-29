from django.conf.urls.defaults import *

# infodict for generic view
info = {
    'app_label'     : 'docs',
    'module_name'   : 'documents',
    'slug_field'    : 'slug',
}

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^(?P<slug>[\w\/]+)/$', 'object_detail', info),
)
