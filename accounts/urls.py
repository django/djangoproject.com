from __future__ import absolute_import

from django.conf.urls import patterns, url, include
from django.contrib.auth import views as auth_views

from registration.forms import RegistrationFormUniqueEmail
from registration import views as registration_views

from . import views as account_views

urlpatterns = patterns('',
    url(
        r'^register/$',
        registration_views.register,
        {
            'backend': 'registration.backends.default.DefaultBackend',
            'form_class': RegistrationFormUniqueEmail,
        },
        name='registration_register',
    ),
    url(
        r'^edit/$',
        account_views.edit_profile,
        name='edit_profile',
    ),
    url(
        r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='auth_password_reset_confim',
    ),
    url(
        r'^reset/done/$',
        auth_views.password_reset_complete,
    ),
    url(r'^_trac/userinfo/$', account_views.json_user_info),
    url(r'', include('registration.backends.default.urls')),
)
