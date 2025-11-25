from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [

    path('',
        TemplateView.as_view(template_name='index.html'),
        name='index'),

    path('accounts/',
        include('registration.backends.admin_approval.urls')),

    path('accounts/profile/',
        TemplateView.as_view(template_name='profile.html'),
        name='profile'),

    path('login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html'),
        name='login'),

    path('admin/',
        admin.site.urls,
        name='admin'),
]
