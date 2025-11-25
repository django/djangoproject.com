"""
URLconf for registration and activation, using django-registration's
default backend.

If the default behavior of these views is acceptable to you, simply
use a line like this in your root URLconf to set up the default URLs
for registration::

    (r'^accounts/', include('registration.backends.default.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

If you'd like to customize registration behavior, feel free to set up
your own URL patterns for these views instead.

"""


from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.views.generic.base import TemplateView

from .views import ActivationView
from .views import RegistrationView
from .views import ResendActivationView

urlpatterns = [
    path('activate/complete/',
         TemplateView.as_view(template_name='registration/activation_complete.html'),
         name='registration_activation_complete'),
    path('activate/resend/',
         ResendActivationView.as_view(),
         name='registration_resend_activation'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    path('activate/<activation_key>/',
         ActivationView.as_view(),
         name='registration_activate'),
    path('register/complete/',
         TemplateView.as_view(template_name='registration/registration_complete.html'),
         name='registration_complete'),
    path('register/closed/',
         TemplateView.as_view(template_name='registration/registration_closed.html'),
         name='registration_disallowed'),
]

if getattr(settings, 'INCLUDE_REGISTER_URL', True):
    urlpatterns += [
        path('register/',
             RegistrationView.as_view(),
             name='registration_register'),
    ]

if getattr(settings, 'INCLUDE_AUTH_URLS', True):
    urlpatterns += [
        path('', include('registration.auth_urls')),
    ]
