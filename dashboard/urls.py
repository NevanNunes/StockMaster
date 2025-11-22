from django.urls import path
from .views import DashboardKPIView, dashboard_view

urlpatterns = [
    path('kpi/', DashboardKPIView.as_view(), name='dashboard-kpi'),
    path('', dashboard_view, name='dashboard-ui'),
]
