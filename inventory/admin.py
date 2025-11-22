from django.contrib import admin
from .models import Warehouse, Location, Category, Product, ProductStock, Operation, OperationLine, StockMovement

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'address')
    search_fields = ('name', 'code')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'warehouse')
    list_filter = ('warehouse',)
    search_fields = ('name', 'code')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'uom', 'min_stock_level')
    list_filter = ('category',)
    search_fields = ('name', 'sku')

@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'location', 'quantity')
    list_filter = ('location__warehouse', 'location')
    search_fields = ('product__name', 'product__sku')

class OperationLineInline(admin.TabularInline):
    model = OperationLine
    extra = 0

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'operation_type', 'status', 'created_at', 'created_by')
    list_filter = ('operation_type', 'status', 'created_at')
    search_fields = ('reference_number',)
    inlines = [OperationLineInline]

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'product', 'transaction_type', 'quantity', 'from_location', 'to_location', 'user')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('product__name', 'product__sku', 'reference_doc__reference_number')
    readonly_fields = ('timestamp', 'user', 'product', 'from_location', 'to_location', 'quantity', 'transaction_type', 'reference_doc')
