from django.db import transaction
from django.db.models import F
from inventory.models import Product, Location, ProductStock, StockMovement, Operation

class StockService:
    @staticmethod
    def _get_or_create_stock(product, location):
        stock, created = ProductStock.objects.get_or_create(
            product=product,
            location=location,
            defaults={'quantity': 0}
        )
        return stock

    @staticmethod
    @transaction.atomic
    def increase_stock(product, location, quantity, operation, user=None):
        """
        Increases stock at a location and logs the movement.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Lock the stock row
        stock = StockService._get_or_create_stock(product, location)
        ProductStock.objects.select_for_update().filter(pk=stock.pk)
        
        stock.quantity = F('quantity') + quantity
        stock.save()
        stock.refresh_from_db()

        # Create Ledger Entry
        StockMovement.objects.create(
            product=product,
            to_location=location,
            quantity=quantity,
            transaction_type=operation.operation_type,
            reference_doc=operation,
            user=user
        )
        return stock

    @staticmethod
    @transaction.atomic
    def decrease_stock(product, location, quantity, operation, user=None):
        """
        Decreases stock at a location and logs the movement.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        stock = StockService._get_or_create_stock(product, location)
        ProductStock.objects.select_for_update().filter(pk=stock.pk)

        if stock.quantity < quantity:
            raise ValueError(f"Insufficient stock for {product.sku} at {location.name}")

        stock.quantity = F('quantity') - quantity
        stock.save()
        stock.refresh_from_db()

        StockMovement.objects.create(
            product=product,
            from_location=location,
            quantity=quantity,
            transaction_type=operation.operation_type,
            reference_doc=operation,
            user=user
        )
        return stock

    @staticmethod
    @transaction.atomic
    def move_stock(product, from_loc, to_loc, quantity, operation, user=None):
        """
        Moves stock from one location to another.
        """
        StockService.decrease_stock(product, from_loc, quantity, operation, user)
        StockService.increase_stock(product, to_loc, quantity, operation, user)

    @staticmethod
    @transaction.atomic
    def adjust_stock(product, location, new_quantity, operation, user=None):
        """
        Adjusts stock to a specific quantity (e.g., after stocktake).
        """
        stock = StockService._get_or_create_stock(product, location)
        ProductStock.objects.select_for_update().filter(pk=stock.pk)
        
        current_qty = stock.quantity
        diff = new_quantity - current_qty
        
        if diff == 0:
            return stock

        stock.quantity = new_quantity
        stock.save()

        # Log the adjustment
        # If diff is positive, it's like a receipt (stock in)
        # If diff is negative, it's like a delivery (stock out)
        if diff > 0:
            StockMovement.objects.create(
                product=product,
                to_location=location,
                quantity=abs(diff),
                transaction_type=Operation.Type.ADJUSTMENT,
                reference_doc=operation,
                user=user
            )
        else:
            StockMovement.objects.create(
                product=product,
                from_location=location,
                quantity=abs(diff),
                transaction_type=Operation.Type.ADJUSTMENT,
                reference_doc=operation,
                user=user
            )
        
        return stock
