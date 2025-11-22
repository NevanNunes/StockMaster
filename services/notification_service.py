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

    @staticmethod
    def notify_transfer_validated(operation) -> None:
        """
        Sends an email notification when a transfer is validated.
        """
        subject = f"🚚 Transfer Validated: {operation.reference_number}"
        
        lines_str = "\n".join([f"- {line.product.sku}: {line.quantity_done} {line.product.uom}" for line in operation.lines.all()])
        
        source = operation.source_location.name if operation.source_location else "Unknown"
        dest = operation.destination_location.name if operation.destination_location else "Unknown"
        user = operation.created_by.username if operation.created_by else 'System'
        
        message = f"""
Transfer Validated

Reference: {operation.reference_number}
From: {source}
To: {dest}
Validated By: {user}
Date: {operation.validated_at}

Items:
{lines_str}

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
            print(f"Failed to send transfer email: {e}")
