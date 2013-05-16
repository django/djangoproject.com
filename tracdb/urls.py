from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(
        r'^bouncing/$',
        views.bouncing_tickets,
        name='bouncing_tickets',
    ),
)
