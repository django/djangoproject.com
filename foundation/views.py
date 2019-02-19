from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, DetailView

from .models import BoardMinutes


# from .forms import BoardMinutesForm


# class BoardMinutesCreateView(CreateView):
#     model = BoardMinutes
#     form_class = BoardMinutesForm


class BoardMinutesRecordListView(ListView):
    model = BoardMinutes
    context_object_name = 'board_minutes_list'


class BoardMinutesDetailView(DetailView):
    model = BoardMinutes
    context_object_name = 'board_minutes'

    def get_object(self, queryset=None):
        return get_object_or_404(BoardMinutes, slug=self.kwargs['slug'])
