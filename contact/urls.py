from django.conf.urls import url
from django.views.generic import TemplateView

from .views import ContactFoundation

urlpatterns = [
    url(r'^foundation/$', ContactFoundation.as_view(), name='contact_foundation'),
    url(r'^sent/$', TemplateView.as_view(template_name='contact/sent.html'), name='contact_form_sent'),
]
