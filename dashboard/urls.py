from django.urls import path
from .views import DashboardKPIView, dashboard_view, DashboardChartsView

urlpatterns = [
    path('kpi/', DashboardKPIView.as_view(), name='dashboard-kpi'),
    path('charts/', DashboardChartsView.as_view(), name='dashboard-charts'),
    path('', dashboard_view, name='dashboard-ui'),
]
