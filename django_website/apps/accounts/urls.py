from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django_website.apps.accounts.forms import RegistrationForm

urlpatterns = patterns('',
    url(
        r'^register/$', 
        "registration.views.register", 
        {'form_class': RegistrationForm},
        name='registration_register',
    ),
    (r'', include('registration.urls')),
)