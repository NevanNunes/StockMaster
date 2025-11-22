from django.urls import path
from .views import stock_ledger_view

# Stock ledger UI routes
urlpatterns = [
    path('', stock_ledger_view, name='stock-ledger'),
]
