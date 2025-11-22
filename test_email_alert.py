"""
Test script to demonstrate the Low Stock Email Alert feature.

This script will:
1. Create a product with a minimum stock level
2. Add stock below the minimum level
3. Trigger a low stock alert email

The email will be printed to the console (development mode).
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockMaster.settings')
django.setup()

from inventory.models import Product, Location, Category, Warehouse
from services.stock_service import StockService

def test_low_stock_email():
    print("=" * 60)
    print("Testing Low Stock Email Alert Feature")
    print("=" * 60)
    
    # Get or create a test product with min stock level
    category, _ = Category.objects.get_or_create(name="Electronics")
    product, created = Product.objects.get_or_create(
        sku="TEST-EMAIL-001",
        defaults={
            'name': 'Test Product for Email',
            'category': category,
            'uom': 'pcs',
            'min_stock_level': 50  # Minimum level is 50
        }
    )
    
    if created:
        print(f"✓ Created test product: {product.name} (SKU: {product.sku})")
    else:
        print(f"✓ Using existing product: {product.name} (SKU: {product.sku})")
    
    print(f"  Minimum stock level: {product.min_stock_level} {product.uom}")
    
    # Get a location
    warehouse = Warehouse.objects.first()
    location = Location.objects.filter(warehouse=warehouse).first()
    print(f"✓ Using location: {location.name} ({location.warehouse.name})")
    
    # Add stock BELOW minimum level to trigger alert
    test_quantity = 30  # Below minimum of 50
    print(f"\n📦 Adding {test_quantity} {product.uom} (BELOW minimum level)")
    print(f"   This should trigger a LOW STOCK ALERT email...")
    print("-" * 60)
    
    # Create a dummy operation for the stock service
    from inventory.models import Operation
    dummy_op = Operation.objects.create(
        operation_type='RECEIPT',
        status='DRAFT'
    )
    
    StockService.increase_stock(
        product=product,
        location=location,
        quantity=test_quantity,
        operation=dummy_op,
        user=None,
        notes="Testing low stock email alert"
    )
    
    print("-" * 60)
    print("\n✅ Check the terminal output above for the email!")
    print("   Look for a message starting with:")
    print("   '⚠️ Low Stock Alert: Test Product for Email'")
    print("\n💡 In production, this would be sent via SMTP to:")
    print(f"   manager@stockmaster.com")
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_low_stock_email()
