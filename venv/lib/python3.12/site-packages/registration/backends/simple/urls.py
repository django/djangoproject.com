"""
URLconf for registration and activation, using django-registration's
one-step backend.

If the default behavior of these views is acceptable to you, simply
use a line like this in your root URLconf to set up the default URLs
for registration::

    (r'^accounts/', include('registration.backends.simple.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

If you'd like to customize registration behavior, feel free to set up
your own URL patterns for these views instead.

"""


from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.views.generic.base import TemplateView

from .views import RegistrationView

urlpatterns = [
    path('register/closed/',
         TemplateView.as_view(template_name='registration/registration_closed.html'),
         name='registration_disallowed'),
]

if getattr(settings, 'INCLUDE_REGISTER_URL', True):
    urlpatterns += [
        path('register/',
             RegistrationView.as_view(
                 success_url=getattr(settings, 'SIMPLE_BACKEND_REDIRECT_URL', '/'),
             ),
             name='registration_register'),
    ]

if getattr(settings, 'INCLUDE_AUTH_URLS', True):
    urlpatterns += [
        path('', include('registration.auth_urls')),
    ]
