from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from . import views

urlpatterns = patterns('',
    url(r'^foundation/$', views.contact_foundation, name='contact_foundation'),
    url(r'^sent/$', TemplateView.as_view(template_name='contact/sent.html'), name='contact_form_sent'),
    url(r'^code-of-conduct/$', views.contact_coc, name='contact_coc'),
)
