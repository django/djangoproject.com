from datetime import timedelta

from .models import START_DATE


def get_week_begin_end_datetimes(day):
    begin = day - timedelta(days=day.weekday())
    end = begin + timedelta(days=7)
    return begin, end


def get_week_number(day):
    monday_start_week = (START_DATE - timedelta(days=START_DATE.weekday()))
    monday_current_week = (day - timedelta(days=day.weekday()))
    return (monday_current_week - monday_start_week).days / 7
