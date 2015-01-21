from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^donate/$', views.donate, name='donate'),
    url(r'^thank-you/(?P<donation>[\w]+)/$', views.thank_you, name='thank-you'),
]
