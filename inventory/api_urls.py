from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet, LocationViewSet, CategoryViewSet, 
    ProductViewSet, OperationViewSet, StockMovementViewSet, PartnerViewSet, LowStockAlertViewSet,
    ReorderReportView
)

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='api-warehouse')
router.register(r'locations', LocationViewSet, basename='api-location')
router.register(r'categories', CategoryViewSet, basename='api-category')
router.register(r'products', ProductViewSet, basename='api-product')
router.register(r'operations', OperationViewSet, basename='api-operation')
router.register(r'movements', StockMovementViewSet, basename='api-movement')
router.register(r'partners', PartnerViewSet, basename='api-partner')
router.register(r'alerts', LowStockAlertViewSet, basename='api-alert')

urlpatterns = [
    path('', include(router.urls)),
    path('reorder-report/', ReorderReportView.as_view(), name='api-reorder-report'),
]
