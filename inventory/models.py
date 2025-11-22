from django.db import models
from django.conf import settings
from django.utils import timezone

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Partner(models.Model):
    class Type(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        SUPPLIER = 'SUPPLIER', 'Supplier'

    name = models.CharField(max_length=100)
    partner_type = models.CharField(max_length=20, choices=Type.choices)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.partner_type})"

class Location(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=50) # e.g., "Rack A", "Shelf 1"
    code = models.CharField(max_length=20)

    class Meta:
        unique_together = ('warehouse', 'code')

    def __str__(self):
        return f"{self.warehouse.code} - {self.name}"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    uom = models.CharField(max_length=20, help_text="Unit of Measure (e.g., kg, pcs)")
    min_stock_level = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"

class ProductStock(models.Model):
    """
    Current stock of a product at a specific location.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('product', 'location')

    def __str__(self):
        return f"{self.product.sku} @ {self.location.code}: {self.quantity}"

class DocumentStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    WAITING = 'WAITING', 'Waiting'
    READY = 'READY', 'Ready'
    DONE = 'DONE', 'Done'
    CANCELED = 'CANCELED', 'Canceled'

class Operation(models.Model):
    class Type(models.TextChoices):
        RECEIPT = 'RECEIPT', 'Receipt'
        DELIVERY = 'DELIVERY', 'Delivery'
        TRANSFER = 'TRANSFER', 'Internal Transfer'
        ADJUSTMENT = 'ADJUSTMENT', 'Stock Adjustment'

    operation_type = models.CharField(max_length=20, choices=Type.choices)
    reference_number = models.CharField(max_length=50, unique=True, blank=True) # Auto-generated
    status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    
    # For transfers
    source_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_operations')
    destination_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_operations')
    
    # For receipts/deliveries
    partner_name = models.CharField(max_length=100, blank=True, help_text="Legacy field for free text name")
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, related_name='operations')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Temporary save to get ID if needed, or use UUID/Timestamp
            # Since we need ID for the format TYPE-ID, we might need to save twice or use another strategy.
            # Let's use a timestamp-based random string or UUID for simplicity in model save, 
            # OR just save, get ID, then update.
            super().save(*args, **kwargs)
            self.reference_number = f"{self.operation_type[:3]}-{self.id:06d}"
            # Save again to update reference_number, ensuring we don't force insert
            kwargs.pop('force_insert', None)
            return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.operation_type} - {self.reference_number} ({self.status})"

class OperationLine(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_demanded = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_done = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.operation.reference_number} - {self.product.sku}"

class StockMovement(models.Model):
    """
    Immutable ledger of all stock moves.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    from_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_out')
    to_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_in')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=Operation.Type.choices)
    reference_doc = models.ForeignKey(Operation, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # New fields for enhanced tracking
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.product.sku}: {self.quantity}"

class LowStockAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='alerts')
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    threshold = models.DecimalField(max_digits=10, decimal_places=2)
    is_resolved = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('product', 'location', 'is_resolved')

    def __str__(self):
        status = "Resolved" if self.is_resolved else "Active"
        return f"ALERT: {self.product.sku} @ {self.location.code} ({status})"
