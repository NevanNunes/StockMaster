from django.db import transaction
from django.db.models import F
from django.utils import timezone
from decimal import Decimal
from typing import Optional
from inventory.models import Product, Location, ProductStock, StockMovement, Operation, LowStockAlert

class StockService:
    """
    Service for handling low-level stock manipulations with robust locking and logging.
    """

    @staticmethod
    def _get_or_create_stock_locked(product: Product, location: Location) -> ProductStock:
        """
        Retrieves or creates a ProductStock entry with a row-level lock.
        Ensures that subsequent updates in the same transaction are safe from race conditions.
        """
        # Use select_for_update() effectively by getting the object inside the lock
        # If it doesn't exist, create it. If it does, lock it.
        stock, created = ProductStock.objects.select_for_update().get_or_create(
            product=product,
            location=location,
            defaults={'quantity': 0}
        )
        return stock

    @staticmethod
    def _check_and_create_low_stock_alert(product: Product, location: Location, current_qty: Decimal) -> None:
        """
        Checks if stock is below threshold and creates an active alert if one doesn't exist.
        """
        if current_qty <= product.min_stock_level:
            # Check if there is already an active alert
            active_alert_exists = LowStockAlert.objects.filter(
                product=product,
                location=location,
                is_resolved=False
            ).exists()

            if not active_alert_exists:
                LowStockAlert.objects.create(
                    product=product,
                    location=location,
                    current_quantity=current_qty,
                    threshold=product.min_stock_level
                )

    @staticmethod
    def _resolve_low_stock_alert(product: Product, location: Location, current_qty: Decimal) -> None:
        """
        Resolves any active low stock alerts if stock is now above threshold.
        """
        if current_qty > product.min_stock_level:
            active_alerts = LowStockAlert.objects.filter(
                product=product,
                location=location,
                is_resolved=False
            )
            if active_alerts.exists():
                active_alerts.update(
                    is_resolved=True,
                    resolved_at=timezone.now(),
                    current_quantity=current_qty # Update with resolving quantity
                )

    @staticmethod
    @transaction.atomic
    def increase_stock(product: Product, location: Location, quantity: Decimal, operation: Operation, user=None, notes: str = "") -> ProductStock:
        """
        Increases stock at a location, logs the movement, and resolves low stock alerts.
        """
        if quantity <= 0:
            raise ValueError(f"Increase quantity must be positive. Got {quantity}")

        # Lock and update
        stock = StockService._get_or_create_stock_locked(product, location)
        stock.quantity = F('quantity') + quantity
        stock.save()
        stock.refresh_from_db()

        # Check for alert resolution
        StockService._resolve_low_stock_alert(product, location, stock.quantity)

        # Create Ledger Entry
        StockMovement.objects.create(
            product=product,
            to_location=location,
            quantity=quantity,
            transaction_type=operation.operation_type,
            reference_doc=operation,
            user=user,
            balance_after=stock.quantity,
            notes=notes
        )
        return stock

    @staticmethod
    @transaction.atomic
    def decrease_stock(product: Product, location: Location, quantity: Decimal, operation: Operation, user=None, notes: str = "") -> ProductStock:
        """
        Decreases stock at a location, logs the movement, and checks for low stock alerts.
        """
        if quantity <= 0:
            raise ValueError(f"Decrease quantity must be positive. Got {quantity}")

        # Lock and update
        stock = StockService._get_or_create_stock_locked(product, location)
        
        if stock.quantity < quantity:
            raise ValueError(f"Insufficient stock for {product.sku} at {location.name}. Available: {stock.quantity}, Requested: {quantity}")

        stock.quantity = F('quantity') - quantity
        stock.save()
        stock.refresh_from_db()

        # Check for low stock
        StockService._check_and_create_low_stock_alert(product, location, stock.quantity)

        # Create Ledger Entry
        StockMovement.objects.create(
            product=product,
            from_location=location,
            quantity=quantity,
            transaction_type=operation.operation_type,
            reference_doc=operation,
            user=user,
            balance_after=stock.quantity,
            notes=notes
        )
        return stock

    @staticmethod
    @transaction.atomic
    def move_stock(product: Product, from_loc: Location, to_loc: Location, quantity: Decimal, operation: Operation, user=None, notes: str = "") -> None:
        """
        Moves stock from one location to another.
        """
        StockService.decrease_stock(product, from_loc, quantity, operation, user, notes=f"Transfer Out: {notes}")
        StockService.increase_stock(product, to_loc, quantity, operation, user, notes=f"Transfer In: {notes}")

    @staticmethod
    @transaction.atomic
    def adjust_stock(product: Product, location: Location, new_quantity: Decimal, operation: Operation, user=None, notes: str = "") -> ProductStock:
        """
        Adjusts stock to a specific quantity (e.g., after stocktake).
        """
        if new_quantity < 0:
             raise ValueError("New quantity cannot be negative")

        stock = StockService._get_or_create_stock_locked(product, location)
        
        current_qty = stock.quantity
        diff = new_quantity - current_qty
        
        if diff == 0:
            return stock

        stock.quantity = new_quantity
        stock.save()
        stock.refresh_from_db()

        # Check alerts
        if diff > 0:
             StockService._resolve_low_stock_alert(product, location, stock.quantity)
        else:
             StockService._check_and_create_low_stock_alert(product, location, stock.quantity)

        # Log the adjustment
        movement_data = {
            'product': product,
            'quantity': abs(diff),
            'transaction_type': Operation.Type.ADJUSTMENT,
            'reference_doc': operation,
            'user': user,
            'balance_after': stock.quantity,
            'notes': notes
        }

        if diff > 0:
            StockMovement.objects.create(to_location=location, **movement_data)
        else:
            StockMovement.objects.create(from_location=location, **movement_data)
        
        return stock
