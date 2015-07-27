from datetime import date

from djangodocs.dev.django.views.generic.list import ListView

from members.models import CorporateMember, DeveloperMember


class DeveloperMemberListView(ListView):
    model = DeveloperMember
    context_object_name = 'members'

    def get_queryset(self):
        return super().get_queryset().filter(member_until=None)

    def get_context_data(self):
        context = super().get_context_data()
        context['former_members'] = DeveloperMember.objects.filter(member_until__lte=date.today())
        return context


class CorporateMemberListView(ListView):
    model = CorporateMember
