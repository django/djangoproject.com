from django.urls import path

from . import views

app_name = 'fundraising'
urlpatterns = [
    path('', views.index, name='index'),
    path('donate/', views.donate, name='donate'),
    path('verify/', views.verify_captcha, name='verify-captcha'),
    path('thank-you/<donation>/', views.thank_you, name='thank-you'),
    path('manage-donations/<hero>/', views.manage_donations, name='manage-donations'),
    path('manage-donations/<hero>/cancel/', views.cancel_donation, name='cancel-donation'),
    path('receive-webhook/', views.receive_webhook, name='receive-webhook'),
    path('update-card/', views.update_card, name='update-card'),
]
