from django.conf.urls import url

from members.views import CorporateMemberListView, DeveloperMemberListView

urlpatterns = [
    url(r'^developer/$', DeveloperMemberListView.as_view(), name='developer_members'),
    url(r'^corporate/$', CorporateMemberListView.as_view(), name='corporate_members'),
]
