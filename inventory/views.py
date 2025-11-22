from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Warehouse, Location, Category, Product, Operation, StockMovement
from .serializers import (
    WarehouseSerializer, LocationSerializer, CategorySerializer, 
    ProductSerializer, OperationSerializer, StockMovementSerializer
)
from services.operation_service import OperationService

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['warehouse']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category']

class OperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all().order_by('-created_at')
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['operation_type', 'status']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        try:
            operation = OperationService.validate_operation(pk, user=request.user)
            serializer = self.get_serializer(operation)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.all().order_by('-timestamp')
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'transaction_type']

from django.shortcuts import render

def product_list_view(request):
    return render(request, 'inventory/product_list.html')

def product_create_view(request):
    return render(request, 'inventory/product_form.html')

def operation_list_view(request, op_type=None):
    return render(request, 'inventory/operation_list.html', {'op_type': op_type})

def operation_create_view(request):
    return render(request, 'inventory/operation_form.html')

def operation_detail_view(request, pk):
    return render(request, 'inventory/operation_detail.html', {'op_id': pk})

def stock_ledger_view(request):
    return render(request, 'inventory/stock_ledger.html')
