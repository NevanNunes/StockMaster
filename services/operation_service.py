from django.db import transaction
from django.utils import timezone
from typing import Optional
from inventory.models import Operation, DocumentStatus
from services.stock_service import StockService

class OperationService:
    """
    Service for handling high-level operation logic, validation, and status transitions.
    """

    VALID_TRANSITIONS = {
        DocumentStatus.DRAFT: [DocumentStatus.WAITING, DocumentStatus.CANCELED],
        DocumentStatus.WAITING: [DocumentStatus.READY, DocumentStatus.CANCELED],
        DocumentStatus.READY: [DocumentStatus.DONE, DocumentStatus.CANCELED],
        DocumentStatus.DONE: [], # Terminal
        DocumentStatus.CANCELED: [], # Terminal
    }

    @staticmethod
    def validate_status_transition(current_status: str, new_status: str) -> bool:
        """
        Checks if a status transition is valid.
        """
        # Allow direct transition to DONE from DRAFT/WAITING/READY for simplicity in this system,
        # unless strict workflow is enforced. For now, let's enforce the map but allow shortcuts if needed.
        # Actually, the requirement says "validate proper status transitions".
        # Let's stick to the map provided in requirements, but usually Validate action jumps to DONE.
        # If the user wants strict flow: Draft -> Waiting -> Ready -> Done.
        # But the current UI has a "Validate" button that likely finalizes it.
        # Let's allow DRAFT/WAITING/READY -> DONE for the 'validate_operation' action specifically.
        
        if new_status == DocumentStatus.DONE:
             return current_status in [DocumentStatus.DRAFT, DocumentStatus.WAITING, DocumentStatus.READY]
        
        allowed = OperationService.VALID_TRANSITIONS.get(current_status, [])
        return new_status in allowed

    @staticmethod
    @transaction.atomic
    def transition_status(operation: Operation, new_status: str, user=None) -> Operation:
        """
        Transitions an operation to a new status if valid.
        """
        if not OperationService.validate_status_transition(operation.status, new_status):
            raise ValueError(f"Invalid status transition from {operation.status} to {new_status}")
        
        operation.status = new_status
        operation.updated_at = timezone.now()
        operation.save()
        return operation

    @staticmethod
    @transaction.atomic
    def validate_operation(operation_id: int, user=None, allow_partial: bool = False) -> Operation:
        """
        Validates an operation and triggers the corresponding stock movements.
        
        Args:
            operation_id: ID of the operation to validate.
            user: User performing the validation.
            allow_partial: If True, allows partial fulfillment when stock is insufficient (for Delivery/Transfer).
        """
        # Lock operation
        operation = Operation.objects.select_for_update().get(pk=operation_id)

        # Check status
        if operation.status == DocumentStatus.DONE:
             raise ValueError(f"Operation {operation.reference_number} is already DONE.")
        
        if operation.status == DocumentStatus.CANCELED:
             raise ValueError(f"Operation {operation.reference_number} is CANCELED and cannot be validated.")

        lines = operation.lines.all()
        if not lines.exists():
            raise ValueError(f"Cannot validate operation {operation.reference_number}: No lines found.")

        # Process based on type
        if operation.operation_type == Operation.Type.RECEIPT:
            if not operation.destination_location:
                raise ValueError(f"Receipt {operation.reference_number} missing destination location.")
            
            for line in lines:
                StockService.increase_stock(
                    product=line.product,
                    location=operation.destination_location,
                    quantity=line.quantity_demanded,
                    operation=operation,
                    user=user,
                    notes=f"Receipt validation"
                )
                line.quantity_done = line.quantity_demanded
                line.save()

        elif operation.operation_type == Operation.Type.DELIVERY:
            if not operation.source_location:
                raise ValueError(f"Delivery {operation.reference_number} missing source location.")

            for line in lines:
                qty_to_process = line.quantity_demanded
                
                # Check availability if partial allowed
                if allow_partial:
                    # We need to check stock without locking first or handle the exception
                    # Better to use the stock service's check or try/catch
                    try:
                         StockService.decrease_stock(
                            product=line.product,
                            location=operation.source_location,
                            quantity=qty_to_process,
                            operation=operation,
                            user=user,
                            notes="Delivery validation"
                        )
                         line.quantity_done = qty_to_process
                    except ValueError:
                        # Insufficient stock, check what we have
                        stock = StockService._get_or_create_stock_locked(line.product, operation.source_location)
                        available = stock.quantity
                        if available > 0:
                            StockService.decrease_stock(
                                product=line.product,
                                location=operation.source_location,
                                quantity=available,
                                operation=operation,
                                user=user,
                                notes=f"Partial Delivery (Requested: {qty_to_process})"
                            )
                            line.quantity_done = available
                        else:
                            line.quantity_done = 0
                else:
                    # Strict full fulfillment
                    StockService.decrease_stock(
                        product=line.product,
                        location=operation.source_location,
                        quantity=qty_to_process,
                        operation=operation,
                        user=user,
                        notes="Delivery validation"
                    )
                    line.quantity_done = qty_to_process
                
                line.save()

        elif operation.operation_type == Operation.Type.TRANSFER:
            if not operation.source_location or not operation.destination_location:
                raise ValueError(f"Transfer {operation.reference_number} requires both source and destination.")

            for line in lines:
                qty_to_process = line.quantity_demanded
                
                if allow_partial:
                     # Similar partial logic for transfer
                    try:
                        StockService.move_stock(
                            product=line.product,
                            from_loc=operation.source_location,
                            to_loc=operation.destination_location,
                            quantity=qty_to_process,
                            operation=operation,
                            user=user,
                            notes="Transfer validation"
                        )
                        line.quantity_done = qty_to_process
                    except ValueError:
                        stock = StockService._get_or_create_stock_locked(line.product, operation.source_location)
                        available = stock.quantity
                        if available > 0:
                            StockService.move_stock(
                                product=line.product,
                                from_loc=operation.source_location,
                                to_loc=operation.destination_location,
                                quantity=available,
                                operation=operation,
                                user=user,
                                notes=f"Partial Transfer (Requested: {qty_to_process})"
                            )
                            line.quantity_done = available
                        else:
                            line.quantity_done = 0
                else:
                    StockService.move_stock(
                        product=line.product,
                        from_loc=operation.source_location,
                        to_loc=operation.destination_location,
                        quantity=qty_to_process,
                        operation=operation,
                        user=user,
                        notes="Transfer validation"
                    )
                    line.quantity_done = qty_to_process
                
                line.save()

        elif operation.operation_type == Operation.Type.ADJUSTMENT:
            if not operation.source_location:
                 raise ValueError(f"Adjustment {operation.reference_number} missing location.")
            
            for line in lines:
                StockService.adjust_stock(
                    product=line.product,
                    location=operation.source_location,
                    new_quantity=line.quantity_demanded,
                    operation=operation,
                    user=user,
                    notes="Stock Adjustment"
                )
                line.quantity_done = line.quantity_demanded
                line.save()

        operation.status = DocumentStatus.DONE
        operation.validated_at = timezone.now()
        operation.save()
        return operation


