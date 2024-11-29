from django.urls import include, path
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail

from . import views as account_views

urlpatterns = [
    path(
        "register/",
        RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
        name="registration_register",
    ),
    path(
        "edit/",
        account_views.edit_profile,
        name="edit_profile",
    ),
    path(
        "delete/",
        account_views.delete_profile,
        name="delete_profile",
    ),
    path(
        "delete/success/",
        account_views.delete_profile_success,
        name="delete_profile_success",
    ),
    path("", include("django.contrib.auth.urls")),
    path("", include("registration.backends.default.urls")),
]
