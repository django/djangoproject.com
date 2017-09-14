from django.urls import path
from django.views.generic import RedirectView, TemplateView

from members.views import (
    CorporateMemberRenewView, CorporateMemberSignUpView,
    IndividualMemberListView, TeamsListView, corporate_member_list_view,
)

app_name = 'members'
urlpatterns = [
    path(
        'developer-members/',
        RedirectView.as_view(pattern_name='members:individual-members'),
        name='developer-members',
    ),
    path('individual-members/', IndividualMemberListView.as_view(), name='individual-members'),
    path('corporate-members/', corporate_member_list_view, name='corporate-members'),
    path('corporate-membership/join/', CorporateMemberSignUpView.as_view(), name='corporate-members-join'),
    path(
        'corporate-membership/renew/<token>/',
        CorporateMemberRenewView.as_view(),
        name='corporate-members-renew',
    ),
    path(
        'corporate-membership/join/thanks/',
        TemplateView.as_view(template_name='members/corporate_members_join_thanks.html'),
        name='corporate-members-join-thanks',
    ),
    path('teams/', TeamsListView.as_view(), name='teams'),
]
