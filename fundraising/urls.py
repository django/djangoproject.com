from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^campaign/(?P<slug>[\w-]+)/$', views.campaign, name='campaign'),
    url(r'^donate/$', views.donate, name='donate'),
    url(r'^thank-you/(?P<donation>[\w]+)/$', views.thank_you, name='thank-you'),
    url(r'^manage_donations/(?P<hero>[\w]+)/$', views.manage_donations, name='manage-donations'),
]
