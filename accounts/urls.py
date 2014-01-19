from __future__ import absolute_import

from django.conf.urls import patterns, url, include
from django.contrib.auth import views as auth_views

from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView

from . import views as account_views

urlpatterns = patterns('',
    url(
        r'^register/$',
        RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
        name='registration_register',
    ),
    url(
        r'^edit/$',
        account_views.edit_profile,
        name='edit_profile',
    ),
    url(r'^_trac/userinfo/$', account_views.json_user_info),
    url(r'', include('django.contrib.auth.urls')),
    url(r'', include('registration.backends.default.urls')),
)
