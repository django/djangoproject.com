from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from contact_form.views import contact_form

from .forms import FoundationContactForm

urlpatterns = patterns('',
    url(
        regex=r'^foundation/$',
        view=contact_form,
        kwargs=dict(
            form_class=FoundationContactForm,
            template_name='contact/foundation.html',
        ),
        name='contact_foundation',
    ),
    url(
        regex=r'^sent/',
        view=TemplateView.as_view(template_name='contact/sent.html'),
        name='contact_form_sent',
    )
)
