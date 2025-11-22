from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet, LocationViewSet, CategoryViewSet, 
    ProductViewSet, OperationViewSet, StockMovementViewSet,
    product_list_view, product_create_view,
    operation_list_view, operation_create_view, operation_detail_view,
    stock_ledger_view
)

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'operations', OperationViewSet)
router.register(r'movements', StockMovementViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('products/', product_list_view, name='product-list'),
    path('products/add/', product_create_view, name='product-create'),
    
    # Operations UI
    path('operations/receipts/', operation_list_view, {'op_type': 'RECEIPT'}, name='receipt-list'),
    path('operations/deliveries/', operation_list_view, {'op_type': 'DELIVERY'}, name='delivery-list'),
    path('operations/transfers/', operation_list_view, {'op_type': 'TRANSFER'}, name='transfer-list'),
    path('operations/adjustments/', operation_list_view, {'op_type': 'ADJUSTMENT'}, name='adjustment-list'),
    path('operations/add/', operation_create_view, name='operation-create'),
    path('operations/<int:pk>/', operation_detail_view, name='operation-detail'),
    
    path('stock-ledger/', stock_ledger_view, name='stock-ledger'),
]
