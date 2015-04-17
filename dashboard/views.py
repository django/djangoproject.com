import datetime
import operator

from django.core.cache import cache
from django.forms.models import model_to_dict
from django.http.response import Http404, JsonResponse
from django.shortcuts import render

from .models import Metric
from .utils import generation_key


def index(request):
    generation = generation_key()
    key = 'dashboard:index'

    data = cache.get(key, version=generation)
    if data is None:
        metrics = []
        for MC in Metric.__subclasses__():
            metrics.extend(MC.objects.filter(show_on_dashboard=True))
        metrics = sorted(metrics, key=operator.attrgetter('display_position'))

        data = []
        for metric in metrics:
            data.append({'metric': metric, 'latest': metric.data.latest()})
        cache.set(key, data, 60 * 60, version=generation)

    return render(request, 'dashboard/index.html', {'data': data})


def metric_detail(request, metric_slug):
    metric = _find_metric_or_404(metric_slug)
    return render(request, 'dashboard/detail.html', {
        'metric': metric,
        'latest': metric.data.latest(),
    })


def metric_json(request, metric_slug):
    metric = _find_metric_or_404(metric_slug)

    try:
        daysback = int(request.GET['days'])
    except (TypeError, KeyError, ValueError):
        daysback = 30

    generation = generation_key()
    key = 'dashboard:metric:%s:%s' % (metric_slug, daysback)

    doc = cache.get(key, version=generation)
    if doc is None:
        start_date = datetime.datetime.now() - datetime.timedelta(days=daysback)

        doc = model_to_dict(metric)
        doc['data'] = metric.gather_data(since=start_date)
        cache.set(key, doc, 60 * 60, version=generation)

    return JsonResponse(doc)


def _find_metric_or_404(slug):
    for MC in Metric.__subclasses__():
        try:
            return MC.objects.get(slug=slug)
        except MC.DoesNotExist:
            continue
    raise Http404('Could not find metric with slug %s' % slug)
