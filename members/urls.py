from django.conf.urls import url

from members.views import CorporateMemberListView  # DeveloperMemberListView

urlpatterns = [
    # Pending population of data.
    # url(r'^developer-members/$', DeveloperMemberListView.as_view(), name='develope-members'),
    url(r'^corporate-members/$', CorporateMemberListView.as_view(), name='corporate-members'),
]
