from django.urls import path

from dashboard import views

urlpatterns = [
    path('', views.index, name="dashboard-index"),
    path('metric/', views.index, name="metric-list"),
    path('metric/<slug:metric_slug>/', views.metric_detail, name="metric-detail"),
    path('metric/<slug:metric_slug>.json', views.metric_json, name="metric-json"),
]
