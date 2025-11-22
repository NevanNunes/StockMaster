from django.urls import path
from .views import operation_list_view, operation_create_view, operation_detail_view

# Operations UI routes
urlpatterns = [
    path('receipts/', operation_list_view, {'op_type': 'RECEIPT'}, name='receipt-list'),
    path('deliveries/', operation_list_view, {'op_type': 'DELIVERY'}, name='delivery-list'),
    path('transfers/', operation_list_view, {'op_type': 'TRANSFER'}, name='transfer-list'),
    path('adjustments/', operation_list_view, {'op_type': 'ADJUSTMENT'}, name='adjustment-list'),
    path('add/', operation_create_view, name='operation-create'),
    path('<int:pk>/', operation_detail_view, name='operation-detail'),
]
