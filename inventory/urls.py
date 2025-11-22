from django.urls import path
from .views import (
    product_list_view, product_create_view,
    operation_list_view, operation_create_view, operation_detail_view,
    stock_ledger_view
)

# HTML UI routes only (API routes are in api_urls.py)
urlpatterns = [
    path('', product_list_view, name='product-list'),
    path('add/', product_create_view, name='product-create'),
]
