import datetime

from django.utils import timezone

_epoc = datetime.datetime(1970, 1, 1, tzinfo=datetime.UTC)


class time_property:
    """
    Convert Trac timestamps into UTC datetimes.

    See http://trac.edgewall.org/browser//branches/0.12-stable/trac/util/datefmt.py
    for Trac's version of all this. Mine's something of a simplification.

    Like the rest of this module this is far from perfect -- no setters, for
    example! That's good enough for now.
    """

    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return timestamp_to_datetime(getattr(instance, self.fieldname))


def datetime_to_timestamp(dt):
    """
    Convert a python datetime object to a Trac-style timestamp.
    """
    return (dt - _epoc).total_seconds() * 1000000


def timestamp_to_datetime(ts):
    """
    Convert a Trac-style timestamp to a python datetime object.
    """
    if ts is None:
        return None
    return _epoc + datetime.timedelta(microseconds=ts)


def dayrange(d, days):
    """
    Return a tuple of two timestamps (Trac-style) corresponding to the bounds
    of the range of `days` days before the given date (included). That is to
    say, `dayrange(TODAY, 1)` will return the range for today, and
    `dayrange(TODAY, 7)` will be the last 7 days.
    """
    if days <= 0:
        raise ValueError(f"days must be greater than 0, not {days!r}")
    if type(d) is not datetime.date:
        raise TypeError(f"d must be a date object, not {d.__class__.__name__}")

    tz = timezone.get_current_timezone()
    start = datetime.datetime.combine(
        d - datetime.timedelta(days=days - 1), datetime.time(0, 0, 0), tzinfo=tz
    )
    end = datetime.datetime.combine(d, datetime.time(23, 59, 59, 999_999), tzinfo=tz)

    return (
        datetime_to_timestamp(start),
        datetime_to_timestamp(end),
    )
