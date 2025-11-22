from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import Warehouse, Location, Category, Product, Operation, OperationLine, StockMovement, DocumentStatus, Partner, LowStockAlert
from .serializers import (
    WarehouseSerializer, LocationSerializer, CategorySerializer, 
    ProductSerializer, OperationSerializer, StockMovementSerializer, PartnerSerializer, LowStockAlertSerializer
)
from .utils import generate_operation_pdf
from services.operation_service import OperationService
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.permissions import IsAuthenticated
from users.permissions import IsManagerOrReadOnly


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
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'sku']
    ordering_fields = ['name', 'sku']

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['partner_type']
    search_fields = ['name', 'email', 'phone']

from .filters import OperationFilter

class OperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all().order_by('-created_at')
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    # permission_classes = [IsAuthenticated]
    
    # Add filter backends
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Use custom FilterSet
    filterset_class = OperationFilter
    
    # Enable search
    search_fields = ['reference_number', 'partner_name', 'partner__name', 'lines__product__sku']
    
    # Enable ordering
    ordering_fields = ['created_at', 'updated_at', 'status']

    def perform_create(self, serializer):
        # For now, allow creation without user
        serializer.save(created_by=None)

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrReadOnly])
    @method_decorator(csrf_exempt)
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
        
        # Return as downloadable file with proper filename
        pdf_bytes = pdf_buffer.getvalue()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{operation.reference_number}.pdf"'
        return response

class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.all().order_by('-timestamp')
    serializer_class = StockMovementSerializer
    # permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'transaction_type']

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from .forms import ProductForm, OperationForm, OperationLineForm

@login_required
def product_list_view(request):
    from django.db.models import Sum, DecimalField
    from django.db.models.functions import Coalesce
    
    queryset = Product.objects.annotate(
        total_quantity=Coalesce(Sum('stocks__quantity'), 0, output_field=DecimalField())
    ).order_by('name')
    
    # Filter by search
    q = request.GET.get('q')
    if q:
        queryset = queryset.filter(name__icontains=q) | queryset.filter(sku__icontains=q)
        
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        queryset = queryset.filter(category_id=category_id)
        
    # Pagination
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'categories': Category.objects.all(),
        'selected_category': request.GET.get('category', ''),  # Add selected category to avoid auto-format issues
    }
    return render(request, 'inventory/product_list.html', context)

@login_required
def product_create_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product-list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
def product_update_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product-list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Optional: Check if product has stock or operations before deleting
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('product-list')

@login_required
def operation_list_view(request, op_type=None):
    queryset = Operation.objects.all().order_by('-created_at')
    
    if op_type:
        queryset = queryset.filter(operation_type=op_type)
        
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
        
    # Pagination
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'receipts': page_obj if op_type == 'RECEIPT' else [], # For receipt_list.html
        'operations': page_obj, # Generic
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'op_type': op_type,
        'selected_status': request.GET.get('status', ''),  # Add selected status to avoid auto-format issues
    }
    
    template_name = 'inventory/operation_list.html'
    if op_type == 'RECEIPT':
        template_name = 'inventory/receipt_list.html'
        
    return render(request, template_name, context)

@login_required
def operation_create_view(request, op_type='RECEIPT'):
    OperationLineFormSet = inlineformset_factory(
        Operation, OperationLine, form=OperationLineForm, extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        form = OperationForm(request.POST)
        formset = OperationLineFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            operation = form.save(commit=False)
            operation.operation_type = op_type
            operation.created_by = request.user
            operation.save()
            
            formset.instance = operation
            formset.save()
            
            messages.success(request, f'{op_type.title()} created successfully.')
            if op_type == 'RECEIPT':
                return redirect('receipt-list')
            return redirect('operation-list') # Generic fallback
    else:
        form = OperationForm()
        formset = OperationLineFormSet()
        
    template_name = 'inventory/operation_form.html'
    if op_type == 'RECEIPT':
        template_name = 'inventory/receipt_form.html'
        
    return render(request, template_name, {
        'form': form,
        'items': formset, # receipt_form uses 'items'
        'formset': formset,
        'op_type': op_type
    })

@login_required
def operation_update_view(request, pk):
    operation = get_object_or_404(Operation, pk=pk)
    OperationLineFormSet = inlineformset_factory(
        Operation, OperationLine, form=OperationLineForm, extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        form = OperationForm(request.POST, instance=operation)
        formset = OperationLineFormSet(request.POST, instance=operation)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Operation updated successfully.')
            if operation.operation_type == 'RECEIPT':
                return redirect('receipt-detail', pk=operation.pk)
            return redirect('operation-detail', pk=operation.pk)
    else:
        form = OperationForm(instance=operation)
        formset = OperationLineFormSet(instance=operation)
        
    template_name = 'inventory/operation_form.html'
    if operation.operation_type == 'RECEIPT':
        template_name = 'inventory/receipt_form.html'
        
    return render(request, template_name, {
        'form': form,
        'items': formset,
        'formset': formset,
        'op_type': operation.operation_type
    })

@login_required
def operation_detail_view(request, pk):
    operation = get_object_or_404(Operation, pk=pk)
    
    template_name = 'inventory/operation_detail.html'
    if operation.operation_type == 'RECEIPT':
        template_name = 'inventory/receipt_detail.html'
        
    return render(request, template_name, {'receipt': operation, 'operation': operation})

@login_required
def operation_validate_view(request, pk):
    operation = get_object_or_404(Operation, pk=pk)
    try:
        OperationService.validate_operation(pk, user=request.user)
        messages.success(request, 'Operation validated successfully.')
    except Exception as e:
        messages.error(request, f'Validation failed: {str(e)}')
        
    if operation.operation_type == 'RECEIPT':
        return redirect('receipt-detail', pk=pk)
    return redirect('operation-detail', pk=pk)

@login_required
def stock_ledger_view(request):
    queryset = StockMovement.objects.all().order_by('-timestamp')
    
    # Filters
    product_id = request.GET.get('product')
    if product_id:
        queryset = queryset.filter(product_id=product_id)
        
    warehouse_id = request.GET.get('warehouse')
    if warehouse_id:
        # StockMovement has from_location and to_location.
        # We should filter if either location belongs to the warehouse.
        queryset = queryset.filter(
            to_location__warehouse_id=warehouse_id
        ) | queryset.filter(
            from_location__warehouse_id=warehouse_id
        )
        
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'movements': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'products': Product.objects.all(),
        'warehouses': Warehouse.objects.all(),
        'selected_product': request.GET.get('product', ''),  # Add to avoid auto-format issues
        'selected_warehouse': request.GET.get('warehouse', ''),  # Add to avoid auto-format issues
    }
    return render(request, 'inventory/stock_ledger.html', context)

@login_required
def reorder_report_view(request):
    return render(request, 'inventory/reorder_report.html')

class LowStockAlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LowStockAlert.objects.all().order_by('-created_at')
    serializer_class = LowStockAlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_resolved', 'is_read']

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        alert = self.get_object()
        alert.is_read = True
        alert.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.queryset.filter(is_read=False, is_resolved=False).count()
        return Response({'count': count})

class ReorderReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.annotate(
            total_quantity=Coalesce(Sum('stocks__quantity'), 0, output_field=DecimalField())
        ).filter(total_quantity__lte=F('min_stock_level'))
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

