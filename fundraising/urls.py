from django.urls import path

from . import views

app_name = "fundraising"
urlpatterns = [
    path("", views.index, name="index"),
    path("donation-session", views.configure_checkout_session, name="donation-session"),
    path("thank-you/", views.thank_you, name="thank-you"),
    path("manage-donations/<hero>/", views.manage_donations, name="manage-donations"),
    path(
        "manage-donations/<hero>/cancel/", views.cancel_donation, name="cancel-donation"
    ),
    path("receive-webhook/", views.receive_webhook, name="receive-webhook"),
    path("update-card/", views.update_card, name="update-card"),
]
