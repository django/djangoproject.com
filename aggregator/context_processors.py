from datetime import date

from django.utils.timesince import timesince

# Take Django's DOB as from the first public blog post.
# https://www.djangoproject.com/weblog/2005/jul/14/prelaunch/
DJANGO_DOB = date(2005, 7, 14)


def community_stats(request):
    """
    Context processor to calculate Django's age for the community pages.
    """
    # Django 3.2 introduces depth kwarg. Set timesince(..., depth=1) then.
    stats = {'age': timesince(DJANGO_DOB)}
    return {'community_stats': stats}
