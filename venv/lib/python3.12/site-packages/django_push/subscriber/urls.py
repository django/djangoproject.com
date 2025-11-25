from django.urls import path

from .views import callback


urlpatterns = [
    path('<int:pk>/', callback, name='subscriber_callback'),
]
