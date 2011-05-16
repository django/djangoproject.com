import functools
from django.views.generic import date_based

from .models import Entry

def prepare_arguments(view):
    @functools.wraps(view)
    def wrapped(request, *args, **kwargs):
        kwargs['allow_future'] = request.user.is_staff
        kwargs['queryset'] = Entry.objects.all() if request.user.is_staff else Entry.objects.published()
        kwargs['date_field'] = 'pub_date'
        return view(request, *args, **kwargs)
    return wrapped

@prepare_arguments
def entry_detail(request, *args, **kwargs):
    return date_based.object_detail(request, *args, **kwargs)

@prepare_arguments
def archive_day(request, *args, **kwargs):
    return date_based.archive_day(request, *args, **kwargs)

@prepare_arguments
def archive_month(request, *args, **kwargs):
    return date_based.archive_month(request, *args, **kwargs)

@prepare_arguments
def archive_year(request, *args, **kwargs):
    return date_based.archive_year(request, *args, **kwargs)

@prepare_arguments
def archive_index(request, *args, **kwargs):
    return date_based.archive_index(request, *args, **kwargs)





