from __future__ import absolute_import

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from contact_form.views import contact_form
from .forms import FoundationContactForm

urlpatterns = patterns('',
    url(
        regex = r'^foundation/$',
        view  = contact_form,
        kwargs = dict(
            form_class = FoundationContactForm,
            template_name = 'contact/foundation.html',
        ),
        name = 'contact_foundation',
    ),
    url(
        regex = r'^sent/',
        view  = direct_to_template,
        kwargs = dict(
            template = 'contact/sent.html',
        ),
        name = 'contact_sent',
    )
)