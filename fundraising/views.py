from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from .forms import AddDjangoHeroForm


def fundraising_index(request):
    return render(request, 'fundraising/index.html', {})


def fundraising_thank_you(request):
    form = AddDjangoHeroForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Thank you! You're a Hero.")
        return redirect(reverse('fundraising'))

    return render(request, 'fundraising/thank-you.html', {'form': form})
