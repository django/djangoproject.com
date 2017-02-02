from django.core import signing
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.dates import timezone_today

from .forms import CorporateMemberSignUpForm
from .models import (
    CORPORATE_MEMBERSHIP_AMOUNTS, CorporateMember, IndividualMember,
)


class IndividualMemberListView(ListView):
    model = IndividualMember
    context_object_name = 'members'

    def get_queryset(self):
        return super().get_queryset().filter(member_until=None)

    def get_context_data(self):
        context = super().get_context_data()
        context['former_members'] = IndividualMember.objects.filter(
            member_until__lte=timezone_today(),
        )
        return context


def corporate_member_list_view(request):
    return render(request, 'members/corporatemember_list.html', {
        'members': CorporateMember.objects.by_membership_level(),
        'corporate_membership_amounts': CORPORATE_MEMBERSHIP_AMOUNTS,
    })


class CorporateMemberSignupMixin(object):
    form_class = CorporateMemberSignUpForm
    model = CorporateMember

    def get_success_url(self):
        return reverse('members:corporate-members-join-thanks')


class CorporateMemberSignUpView(CorporateMemberSignupMixin, CreateView):
    pass


class CorporateMemberRenewView(CorporateMemberSignupMixin, UpdateView):

    def get_object(self):
        """
        Convert the token back to a pk and check that it's not older than
        14 days.
        """
        try:
            pk = signing.loads(self.kwargs['token'], max_age=1.21e+6)
        except signing.BadSignature:
            raise Http404(
                "No %(verbose_name)s found matching the query" %
                {'verbose_name': self.model._meta.verbose_name}
            )
        return self.get_queryset().get(pk=pk)
