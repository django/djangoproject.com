import datetime
import operator

from django.core.cache import cache
from django.forms.models import model_to_dict
from django.http.response import Http404, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

from .models import Metric
from .utils import generation_key


def index(request):
    generation = generation_key()
    key = "dashboard:index"

    data = cache.get(key, version=generation)
    if data is None:
        data = [m for MC in Metric.__subclasses__() for m in MC.objects.for_dashboard()]
        data.sort(key=operator.attrgetter("display_position"))
        cache.set(key, data, 60 * 60, version=generation)

    # Due to the way `with_latest()` is implemented, the timestamps we get back
    # are actually strings (because JSON) so they need converting to proper
    # datetime objects first.
    timestamps = [
        datetime.datetime.fromisoformat(m.latest["timestamp"])
        for m in data
        if m.latest is not None
    ]
    last_updated = max(timestamps, default=None)

    return render(
        request, "dashboard/index.html", {"data": data, "last_updated": last_updated}
    )


def metric_detail(request, metric_slug):
    metric = _find_metric_or_404(metric_slug)
    return render(
        request,
        "dashboard/detail.html",
        {
            "metric": metric,
            "latest": metric.data.latest(),
        },
    )


def metric_json(request, metric_slug):
    metric = _find_metric_or_404(metric_slug)

    try:
        daysback = int(request.GET["days"])
    except (TypeError, KeyError, ValueError):
        daysback = 30

    generation = generation_key()
    key = f"dashboard:metric:{metric_slug}:{daysback}"

    doc = cache.get(key, version=generation)
    if doc is None:
        start_date = datetime.datetime.now() - datetime.timedelta(days=daysback)

        doc = model_to_dict(metric)
        doc["data"] = metric.gather_data(since=start_date)
        cache.set(key, doc, 60 * 60, version=generation)

    return JsonResponse(doc)


def _find_metric_or_404(slug):
    for MC in Metric.__subclasses__():
        try:
            return MC.objects.get(slug=slug)
        except MC.DoesNotExist:
            continue
    raise Http404(_("Could not find metric with slug %s") % slug)
