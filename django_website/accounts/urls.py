from __future__ import absolute_import

from django.conf.urls.defaults import patterns, url, include
from registration.forms import RegistrationFormUniqueEmail

urlpatterns = patterns('',
    url(
        r'^register/$',
        "registration.views.register",
        {'form_class': RegistrationFormUniqueEmail},
        name='registration_register',
    ),
    url(
        r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='auth_password_reset_confim',
    ),
    url(
        r'^reset/done/$',
        'django.contrib.auth.views.password_reset_complete'
    ),
    (r'', include('registration.urls')),
)
