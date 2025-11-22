from django.urls import path
from .views import (
    operation_list_view, operation_create_view, operation_detail_view,
    operation_update_view, operation_validate_view
)

# Operations UI routes
urlpatterns = [
    # Generic Operation Routes
    path('add/', operation_create_view, name='operation-create'),
    path('<int:pk>/', operation_detail_view, name='operation-detail'),
    path('<int:pk>/edit/', operation_update_view, name='operation-update'),

    # Receipt Routes
    path('receipts/', operation_list_view, {'op_type': 'RECEIPT'}, name='receipt-list'),
    path('receipts/create/', operation_create_view, {'op_type': 'RECEIPT'}, name='receipt-create'),
    path('receipts/<int:pk>/', operation_detail_view, name='receipt-detail'),
    path('receipts/<int:pk>/edit/', operation_update_view, name='receipt-update'),
    path('receipts/<int:pk>/validate/', operation_validate_view, name='receipt-validate'),

    # Delivery Routes
    path('deliveries/', operation_list_view, {'op_type': 'DELIVERY'}, name='delivery-list'),
    path('deliveries/create/', operation_create_view, {'op_type': 'DELIVERY'}, name='delivery-create'),
    path('deliveries/<int:pk>/', operation_detail_view, name='delivery-detail'),
    path('deliveries/<int:pk>/edit/', operation_update_view, name='delivery-update'),
    
    # Transfer Routes
    path('transfers/', operation_list_view, {'op_type': 'TRANSFER'}, name='transfer-list'),
    path('transfers/create/', operation_create_view, {'op_type': 'TRANSFER'}, name='transfer-create'),
    path('transfers/<int:pk>/', operation_detail_view, name='transfer-detail'),
    path('transfers/<int:pk>/edit/', operation_update_view, name='transfer-update'),
    
    # Adjustment Routes
    path('adjustments/', operation_list_view, {'op_type': 'ADJUSTMENT'}, name='adjustment-list'),
    path('adjustments/create/', operation_create_view, {'op_type': 'ADJUSTMENT'}, name='adjustment-create'),
    path('adjustments/<int:pk>/', operation_detail_view, name='adjustment-detail'),
    path('adjustments/<int:pk>/edit/', operation_update_view, name='adjustment-update'),
]
