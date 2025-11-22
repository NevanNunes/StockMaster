from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.http import HttpResponse
from .models import Warehouse, Location, Category, Product, Operation, StockMovement, DocumentStatus
from .serializers import (
    WarehouseSerializer, LocationSerializer, CategorySerializer, 
    ProductSerializer, OperationSerializer, StockMovementSerializer
)
from .utils import generate_operation_pdf
from services.operation_service import OperationService

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    # permission_classes = [IsAuthenticated]

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    # permission_classes = [IsAuthenticated]
    filterset_fields = ['warehouse']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]
    filterset_fields = ['category']

class OperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all().order_by('-created_at')
    serializer_class = OperationSerializer
    # permission_classes = [IsAuthenticated]
    filterset_fields = ['operation_type', 'status']

    def perform_create(self, serializer):
        # For now, allow creation without user
        serializer.save(created_by=None)

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        try:
            # Pass None for user if not authenticated
            user = getattr(request, 'user', None) if hasattr(request, 'user') and request.user.is_authenticated else None
            operation = OperationService.validate_operation(pk, user=user)
            serializer = self.get_serializer(operation)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """
        Generate and download PDF for this operation.
        URL: /api/inventory/operations/<id>/pdf/
        """
        operation = self.get_object()
        
        # Only allow PDF for validated operations
        if operation.status != DocumentStatus.DONE:
            return Response(
                {'error': 'PDF only available for validated operations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate PDF
        pdf_buffer = generate_operation_pdf(operation)
        
        # Return as downloadable file
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{operation.reference_number}.pdf"'
        return response        

class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.all().order_by('-timestamp')
    serializer_class = StockMovementSerializer
    # permission_classes = [IsAuthenticated]
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
