# -*- coding: utf-8 -*-
from django.conf.urls import url

urlpatterns = [
    url('^$', 'dashboard.views.index', name="dashboard-index"),
    url('^metric/([\w-]+)/$', 'dashboard.views.metric_detail', name="metric-detail"),
    url('^metric/([\w-]+).json$', 'dashboard.views.metric_json', name="metric-json"),
]
