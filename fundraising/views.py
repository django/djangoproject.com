from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.shortcuts import redirect, render

from .forms import AddDjangoHeroForm
from .models import DjangoHero, Donation, WEEKLY_GOAL
from .utils import get_week_begin_end_datetimes, get_week_number


def fundraising_index(request):
    begin, end = get_week_begin_end_datetimes(date.today())
    donated_amount = Donation.objects.filter(
        date__gte=begin, date__lt=end,
    ).aggregate(Sum('amount'))

    donors_with_logo = DjangoHero.objects.in_period(begin, end, with_logo=True)
    other_donors = DjangoHero.objects.in_period(begin, end)
    total_donors = len(donors_with_logo) + len(other_donors)

    return render(request, 'fundraising/index.html', {
        'donated_amount': donated_amount['amount__sum'] or Decimal("0.00"),
        'goal_amount': WEEKLY_GOAL,
        'week_number': get_week_number(date.today()),
        'donors_with_logo': donors_with_logo,
        'other_donors': other_donors,
        'total_donors': total_donors,
    })


def fundraising_thank_you(request):
    form = AddDjangoHeroForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Thank you! You're a Hero.")
        return redirect(reverse('fundraising'))

    return render(request, 'fundraising/thank-you.html', {'form': form})
