from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView

from members.views import (
    CorporateMemberRenewView, CorporateMemberSignUpView,
    IndividualMemberListView, TeamsListView, corporate_member_list_view,
)

app_name = 'members'
urlpatterns = [
    url(
        r'^developer-members/$',
        RedirectView.as_view(pattern_name='members:individual-members'),
        name='developer-members',
    ),
    url(r'^individual-members/$', IndividualMemberListView.as_view(), name='individual-members'),
    url(r'^corporate-members/$', corporate_member_list_view, name='corporate-members'),
    url(r'^corporate-membership/join/$', CorporateMemberSignUpView.as_view(), name='corporate-members-join'),
    url(
        r'^corporate-membership/renew/(?P<token>[A-Za-z0-9:_-]+)/$',
        CorporateMemberRenewView.as_view(),
        name='corporate-members-renew',
    ),
    url(
        r'^corporate-membership/join/thanks/$',
        TemplateView.as_view(template_name='members/corporate_members_join_thanks.html'),
        name='corporate-members-join-thanks',
    ),
    url('^teams/$', TeamsListView.as_view(), name='teams'),
]
