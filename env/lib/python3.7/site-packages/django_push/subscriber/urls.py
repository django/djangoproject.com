from django.conf.urls import url

from .views import callback


urlpatterns = [
    url(r'^(?P<pk>\d+)/$', callback, name='subscriber_callback'),
]
