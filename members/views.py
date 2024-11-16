from django.core import signing
from django.db.models import Count, Prefetch
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, ListView, TemplateView, UpdateView
from django.views.generic.dates import timezone_today

from .forms import CorporateMemberSignUpForm
from .models import (
    CORPORATE_MEMBERSHIP_AMOUNTS,
    CorporateMember,
    IndividualMember,
    PreviousTeamMembership,
    Team,
)


class IndividualMemberListView(ListView):
    model = IndividualMember
    context_object_name = "members"

    def get_queryset(self):
        return super().get_queryset().filter(member_until=None)

    def get_context_data(self):
        context = super().get_context_data()
        context["former_members"] = IndividualMember.objects.filter(
            member_until__lte=timezone_today(),
        )
        return context


def corporate_member_list_view(request):
    return render(
        request,
        "members/corporatemember_list.html",
        {
            "members": CorporateMember.objects.by_membership_level(),
            "corporate_membership_amounts": CORPORATE_MEMBERSHIP_AMOUNTS,
        },
    )


class CorporateMemberSignupMixin:
    form_class = CorporateMemberSignUpForm
    model = CorporateMember

    def get_success_url(self):
        return reverse("members:corporate-members-join-thanks")


class CorporateMemberSignUpView(CorporateMemberSignupMixin, CreateView):
    pass


class CorporateMemberRenewView(CorporateMemberSignupMixin, UpdateView):
    def get_object(self):
        """
        Convert the token back to a pk and check that it's not older than
        30 days.
        """
        try:
            pk = signing.loads(self.kwargs["token"], max_age=2.592e6)
        except signing.BadSignature:
            raise Http404(
                "No %(verbose_name)s found matching the query"
                % {"verbose_name": self.model._meta.verbose_name}
            )
        return self.get_queryset().get(pk=pk)


class CorporateMemberBadgesView(TemplateView):
    template_name = "members/corporate_member_badges.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        levels = ["bronze", "silver", "gold", "platinum"]
        img_variants = ["", "g", "b", "w"]

        badges = {}
        for level in levels:
            badges[level] = []
            for variant in img_variants:
                basename = f"{level}_{variant}" if variant else level
                filename = f"img/badges/corporate_members/{basename}"
                badges[level].append(
                    {
                        "svg": f"{filename}.svg",
                        "png": f"{filename}.png",
                    }
                )

        context["badges"] = badges
        return context


class TeamsListView(ListView):
    model = Team
    context_object_name = "teams"

    def get_queryset(self):
        return (
            self.model.objects.filter(archived=False)
            .prefetch_related("members")
            .order_by("name")
        )


class TeamsArchiveView(TemplateView):
    template_name = "members/team_archive.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        previous_team_membership_qs = PreviousTeamMembership.objects.select_related(
            "member"
        )
        archived_teams = (
            Team.objects.filter(archived=True)
            .prefetch_related(
                "members",
                Prefetch(
                    "previousteammembership_set",
                    queryset=previous_team_membership_qs,
                ),
            )
            .order_by("name")
        )

        # Active teams with former members.
        teams = (
            Team.objects.prefetch_related(
                Prefetch(
                    "previousteammembership_set",
                    queryset=previous_team_membership_qs,
                )
            )
            .annotate(former_member_count=Count("former_members", distinct=True))
            .filter(former_member_count__gt=0, archived=False)
            .order_by("name")
        )

        context["teams"] = teams
        context["archived_teams"] = archived_teams
        return context
