from django.conf.urls import url

from dashboard import views

urlpatterns = [
    url(r'^$', views.index, name="dashboard-index"),
    url(r'^metric/$', views.index, name="metric-list"),
    url(r'^metric/([\w-]+)/$', views.metric_detail, name="metric-detail"),
    url(r'^metric/([\w-]+).json$', views.metric_json, name="metric-json"),
]
