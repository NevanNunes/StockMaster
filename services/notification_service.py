from django.core.mail import send_mail
from django.conf import settings
from inventory.models import Product, Location
from decimal import Decimal


class NotificationService:
    """
    Service for handling notifications (email, SMS, etc.)
    """
    
    @staticmethod
    def notify_low_stock(product: Product, location: Location, current_qty: Decimal) -> None:
        """
        Sends an email notification when stock falls below minimum level.
        
        Args:
            product: The product with low stock
            location: The location where stock is low
            current_qty: Current quantity in stock
        """
        if current_qty > product.min_stock_level:
            # Don't send email if stock is above minimum
            return
        
        subject = f"⚠️ Low Stock Alert: {product.name} ({product.sku})"
        
        message = f"""
Low Stock Alert

Product: {product.name}
SKU: {product.sku}
Location: {location.name} ({location.warehouse.name})
Current Quantity: {current_qty} {product.uom}
Minimum Level: {product.min_stock_level} {product.uom}

⚠️ Stock is below minimum level. Please reorder immediately.

---
StockMaster Inventory Management System
"""
        
        recipient_list = [settings.MANAGER_EMAIL]
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't crash the transaction
            print(f"Failed to send low stock email: {e}")
