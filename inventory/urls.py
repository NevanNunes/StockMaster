from django.urls import path
from .views import (
    product_list_view, product_create_view, product_update_view, product_delete_view,
    reorder_report_view,
    operation_list_view, operation_create_view, operation_detail_view, operation_update_view, operation_validate_view
)

urlpatterns = [
    path('', product_list_view, name='product-list'),
    path('add/', product_create_view, name='product-create'),
    path('<int:pk>/edit/', product_update_view, name='product-update'),
    path('<int:pk>/delete/', product_delete_view, name='product-delete'),
    path('reorder-report/', reorder_report_view, name='reorder-report'),
    
    # Operations
    path('operations/', operation_list_view, name='operation-list'),
    path('operations/create/<str:op_type>/', operation_create_view, name='operation-create'),
    path('operations/<int:pk>/', operation_detail_view, name='operation-detail'),
    path('operations/<int:pk>/edit/', operation_update_view, name='operation-update'),
    path('operations/<int:pk>/validate/', operation_validate_view, name='operation-validate'),
    
    # Receipt specific URLs (aliasing to generic views or specific ones if needed)
    path('receipts/', lambda r: operation_list_view(r, 'RECEIPT'), name='receipt-list'),
    path('receipts/create/', lambda r: operation_create_view(r, 'RECEIPT'), name='receipt-create'),
    path('receipts/<int:pk>/', operation_detail_view, name='receipt-detail'),
    path('receipts/<int:pk>/edit/', operation_update_view, name='receipt-update'),
    path('receipts/<int:pk>/validate/', operation_validate_view, name='receipt-validate'),
]

from rest_framework.routers import DefaultRouter
from .views import LowStockAlertViewSet

router = DefaultRouter()
router.register(r'api/alerts', LowStockAlertViewSet, basename='alert')

urlpatterns += router.urls
