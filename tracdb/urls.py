from django.urls import path

from . import views

urlpatterns = [
    path('bouncing/', views.bouncing_tickets, name='bouncing_tickets'),
]
