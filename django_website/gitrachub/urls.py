from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^webhook/$', views.GithubWebhook.as_view(), name='github_webhook'),
    url(r'^pulls/(?P<ticket_id>\d+)/$',
        views.PullRequestsForTicket.as_view(), name='pull_requests_for_ticket'),
)
