"""
Example URLConf for a contact form with Akismet spam filtering.

If all you want is the basic contact-form plus spam filtering,
include this URLConf somewhere in your URL hierarchy (for example, at
``/contact/``).

"""

# SPDX-License-Identifier: BSD-3-Clause

from django.urls import path
from django.views.generic import TemplateView

from .forms import AkismetContactForm
from .views import ContactFormView

urlpatterns = [
    path(
        "",
        ContactFormView.as_view(form_class=AkismetContactForm),
        name="django_contact_form",
    ),
    path(
        "sent/",
        TemplateView.as_view(
            template_name="django_contact_form/contact_form_sent.html"
        ),
        name="django_contact_form_sent",
    ),
]
