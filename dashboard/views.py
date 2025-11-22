from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q, F
from inventory.models import Product, Operation, DocumentStatus, ProductStock

class DashboardKPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Total Products
        total_products = Product.objects.count()

        # 2. Low Stock Items (Global check - if total stock across all warehouses < min_stock)
        # This is a bit complex if min_stock is per product globally. 
        # Let's assume min_stock_level is global for the product.
        # We need to annotate total quantity first.
        low_stock_count = 0
        out_of_stock_count = 0
        
        products = Product.objects.annotate(total_qty=Sum('stocks__quantity'))
        for p in products:
            qty = p.total_qty or 0
            if qty == 0:
                out_of_stock_count += 1
            elif qty < p.min_stock_level:
                low_stock_count += 1

        # 3. Pending Operations
        pending_receipts = Operation.objects.filter(
            operation_type=Operation.Type.RECEIPT, 
            status__in=[DocumentStatus.DRAFT, DocumentStatus.WAITING, DocumentStatus.READY]
        ).count()

        pending_deliveries = Operation.objects.filter(
            operation_type=Operation.Type.DELIVERY, 
            status__in=[DocumentStatus.DRAFT, DocumentStatus.WAITING, DocumentStatus.READY]
        ).count()

        pending_transfers = Operation.objects.filter(
            operation_type=Operation.Type.TRANSFER, 
            status__in=[DocumentStatus.DRAFT, DocumentStatus.WAITING, DocumentStatus.READY]
        ).count()

        data = {
            'total_products': total_products,
            'low_stock_items': low_stock_count,
            'out_of_stock_items': out_of_stock_count,
            'pending_receipts': pending_receipts,
            'pending_deliveries': pending_deliveries,
            'pending_transfers': pending_transfers,
        }
        return Response(data)

from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'dashboard/index.html')
