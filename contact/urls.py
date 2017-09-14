from django.urls import path
from django.views.generic import TemplateView

from .views import ContactFoundation

urlpatterns = [
    path('foundation/', ContactFoundation.as_view(), name='contact_foundation'),
    path('sent/', TemplateView.as_view(template_name='contact/sent.html'), name='contact_form_sent'),
]
