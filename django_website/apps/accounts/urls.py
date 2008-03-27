from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from registration.forms import RegistrationFormUniqueEmail

urlpatterns = patterns('',
    url(
        r'^register/$', 
        "registration.views.register", 
        {'form_class': RegistrationFormUniqueEmail},
        name='registration_register',
    ),
    (r'', include('registration.urls')),
)
