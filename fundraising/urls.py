from django.conf.urls import url

from . import views

app_name = 'fundraising'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^donate/$', views.donate, name='donate'),
    url(r'^thank-you/(?P<donation>[\w]+)/$', views.thank_you, name='thank-you'),
    url(r'^manage-donations/(?P<hero>[\w]+)/$', views.manage_donations, name='manage-donations'),
    url(r'^manage-donations/(?P<hero>[\w]+)/cancel/$', views.cancel_donation, name='cancel-donation'),
    url(r'^receive-webhook/$', views.receive_webhook, name='receive-webhook'),
    url(r'^update-card/$', views.update_card, name='update-card'),
]
