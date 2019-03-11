from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from .models import BoardMinutes


class BoardMinutesRecordListView(ListView):
    model = BoardMinutes
    context_object_name = 'board_minutes_list'


class BoardMinutesDetailView(DetailView):
    model = BoardMinutes
    context_object_name = 'board_minutes'

    def get_object(self, queryset=None):
        return get_object_or_404(BoardMinutes, slug=self.kwargs['slug'])
