from django.conf.urls import url
from django.views.generic import TemplateView

from members.views import (
    CorporateMemberListView, CorporateMemberSignUpView,
    DeveloperMemberListView,
)

app_name = 'members'
urlpatterns = [
    url(r'^developer-members/$', DeveloperMemberListView.as_view(), name='developer-members'),
    url(r'^corporate-members/$', CorporateMemberListView.as_view(), name='corporate-members'),
    url(r'^corporate-membership/join/$', CorporateMemberSignUpView.as_view(), name='corporate-members-join'),
    url(
        r'^corporate-membership/join/thanks/$',
        TemplateView.as_view(template_name='members/corporate_members_join_thanks.html'),
        name='corporate-members-join-thanks',
    ),
]
