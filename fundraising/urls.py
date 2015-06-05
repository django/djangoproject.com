from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^campaign/(?P<slug>[\w-]+)/$', views.campaign, name='campaign'),
    url(r'^donate/$', views.donate, name='donate'),
    url(r'^thank-you/(?P<donation>[\w]+)/$', views.thank_you, name='thank-you'),
    url(r'^manage-donations/(?P<hero>[\w]+)/$', views.manage_donations, name='manage-donations'),
    url(r'^manage-donations/(?P<hero>[\w]+)/cancel/(?P<donation>[\w]+)$', views.cancel_donation, name='cancel-donation'),
    url(r'^receive_webhook/', views.receive_webhook, name='receive-webhook'),
    url(r'^update_card/', views.update_card, name='update-card'),
]
