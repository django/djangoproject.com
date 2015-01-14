from __future__ import absolute_import
import datetime
import operator

from django.http.response import JsonResponse, Http404
from django.shortcuts import render
from django.forms.models import model_to_dict

from .models import Metric


def index(request):
    metrics = []
    for MC in Metric.__subclasses__():
        metrics.extend(MC.objects.filter(show_on_dashboard=True))
    metrics = sorted(metrics, key=operator.attrgetter('display_position'))

    data = []
    for metric in metrics:
        data.append({'metric': metric, 'latest': metric.data.latest()})
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
    start_date = datetime.datetime.now() - datetime.timedelta(days=daysback)

    doc = model_to_dict(metric)
    doc['data'] = metric.gather_data(since=start_date)

    return JsonResponse(doc)


def _find_metric_or_404(slug):
    for MC in Metric.__subclasses__():
        try:
            return MC.objects.get(slug=slug)
        except MC.DoesNotExist:
            continue
    raise Http404('Could not find metric with slug %s' % slug)
