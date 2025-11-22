from django.urls import path
from .views import (
    product_list_view, product_create_view, product_update_view, product_delete_view,
    reorder_report_view
)

urlpatterns = [
    path('', product_list_view, name='product-list'),
    path('add/', product_create_view, name='product-create'),
    path('<int:pk>/edit/', product_update_view, name='product-update'),
    path('<int:pk>/delete/', product_delete_view, name='product-delete'),
    path('reorder-report/', reorder_report_view, name='reorder-report'),
]
