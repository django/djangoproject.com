import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.forms.models import model_to_dict
from django.http.response import Http404, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

from .models import Datum, Metric
from .utils import generation_key


def index(request):
    generation = generation_key()
    key = "dashboard:index"

    data = cache.get(key, version=generation)
    if data is None:
        metrics = []
        for MC in Metric.__subclasses__():
            metrics.extend(
                MC.objects.filter(show_on_dashboard=True).select_related("category")
            )

        content_types = ContentType.objects.get_for_models(*metrics)
        datum_queryset = Datum.objects.none()
        for metric, content_type in content_types.items():
            datum_queryset = datum_queryset.union(
                Datum.objects.filter(
                    content_type_id=content_type.id, object_id=metric.id
                )
                .order_by("-timestamp")[0:1]
            )

        latest_datums = {
            (datum.object_id, datum.content_type_id): datum for datum in datum_queryset
        }

        data = []
        for metric, content_type in content_types.items():
            if latest := latest_datums.get((metric.id, content_type.id)):
                data.append({"metric": metric, "latest": latest})
        data = sorted(data, key=lambda elem: elem["metric"].display_position)
        cache.set(key, data, 60 * 60, version=generation)

    return render(request, "dashboard/index.html", {"data": data})


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
