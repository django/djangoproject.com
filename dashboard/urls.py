# -*- coding: utf-8 -*-
from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'dashboard.views.index', name="dashboard-index"),
    url(r'^metric/$', 'dashboard.views.index', name="metric-list"),
    url(r'^metric/([\w-]+)/$', 'dashboard.views.metric_detail', name="metric-detail"),
    url(r'^metric/([\w-]+).json$', 'dashboard.views.metric_json', name="metric-json"),
]
