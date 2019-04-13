"""
Example URLConf for a contact form with Akismet spam filtering.

If all you want is the basic contact-form plus spam filtering,
include this URLConf somewhere in your URL hierarchy (for example, at
``/contact/``).

"""

from django.conf.urls import url
from django.views.generic import TemplateView

from .forms import AkismetContactForm
from .views import ContactFormView


urlpatterns = [
    url(r'^$',
        ContactFormView.as_view(
            form_class=AkismetContactForm),
        name='contact_form'),
    url(r'^sent/$',
        TemplateView.as_view(
            template_name='contact_form/contact_form_sent.html'),
        name='contact_form_sent'),
]
