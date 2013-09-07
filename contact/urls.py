from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from .views import ContactFoundation

urlpatterns = patterns('',
    url(r'^foundation/$', ContactFoundation.as_view(), name='contact_foundation'),
    url(r'^sent/$', TemplateView.as_view(template_name='contact/sent.html'), name='contact_form_sent'),
)
