from django.urls import path

from . import views

urlpatterns = [
    path("bouncing/", views.bouncing_tickets, name="bouncing_tickets"),
    path("api/tickets/<int:ticket_id>", views.api_ticket, name="api_ticket"),
]
