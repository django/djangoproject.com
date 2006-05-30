from django.conf.urls.defaults import *
from models import Document # relative import

info_dict = {
    'queryset': Document.objects.all(),
    'slug_field': 'slug',
}

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^(?P<slug>[\w\/]+)/$', 'object_detail', info_dict),
)
