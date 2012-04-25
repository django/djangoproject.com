from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^webhook/$', views.GithubWebhook.as_view(), name='github_webhook')
)
