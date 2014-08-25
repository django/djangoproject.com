from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^bouncing/$',
        views.bouncing_tickets,
        name='bouncing_tickets',
    ),
]
