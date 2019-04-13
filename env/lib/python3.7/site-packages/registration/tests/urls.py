"""
URLs used in the unit tests for django-registration.

You should not attempt to use these URLs in any sort of real or
development environment; instead, use
``registration/backends/default/urls.py``. This URLconf includes those
URLs, and also adds several additional URLs which serve no purpose
other than to test that optional keyword arguments are properly
handled.

"""

from django.conf.urls import include
from django.conf.urls import url
from django.views.generic import TemplateView

from registration.views import ActivationView
from registration.views import RegistrationView

urlpatterns = [
    # Test the 'activate' view with custom template
    # name.
    url(r'^activate-with-template-name/(?P<activation_key>\w+)/$',
        ActivationView.as_view(),
        {'template_name': 'registration/test_template_name.html',
         'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_test_activate_template_name'),
    # Test the 'activate' view with
    # extra_context_argument.
    url(r'^activate-extra-context/(?P<activation_key>\w+)/$',
        ActivationView.as_view(),
        {'extra_context': {'foo': 'bar', 'callable': lambda: 'called'},
         'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_test_activate_extra_context'),
    # Test the 'activate' view with success_url argument.
    url(r'^activate-with-success-url/(?P<activation_key>\w+)/$',
        ActivationView.as_view(),
        {'success_url': 'registration_test_custom_success_url',
         'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_test_activate_success_url'),
    # Test the 'register' view with custom template
    # name.
    url(r'^register-with-template-name/$',
        RegistrationView.as_view(),
        {'template_name': 'registration/test_template_name.html',
         'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_test_register_template_name'),
    # Test the'register' view with extra_context
    # argument.
    url(r'^register-extra-context/$',
        RegistrationView.as_view(),
        {'extra_context': {'foo': 'bar', 'callable': lambda: 'called'},
         'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_test_register_extra_context'),
    # Test the 'register' view with custom URL for
    # closed registration.
    url(r'^register-with-disallowed-url/$',
        RegistrationView.as_view(),
        {'disallowed_url': 'registration_test_custom_disallowed',
         'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_test_register_disallowed_url'),
    # Set up a pattern which will correspond to the
    # custom 'disallowed_url' above.
    url(r'^custom-disallowed/$',
        TemplateView.as_view(template_name='registration/registration_closed.html'),
        name='registration_test_custom_disallowed'),
    # Test the 'register' view with custom redirect
    # on successful registration.
    url(r'^register-with-success_url/$',
        RegistrationView.as_view(),
        {'success_url': 'registration_test_custom_success_url',
         'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_test_register_success_url'),
    # Pattern for custom redirect set above.
    url(r'^custom-success/$',
        TemplateView.as_view(template_name='registration/test_template_name.html'),
        name='registration_test_custom_success_url'),
    url(r'', include('registration.backends.default.urls')),
]
