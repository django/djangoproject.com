from django.shortcuts import render


def gone(request, *args, **kwargs):
    """
    Display a nice 410 gone page.
    """
    return render(request, '410.html', status=410)
