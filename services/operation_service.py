from django.db import transaction
from django.utils import timezone
from inventory.models import Operation, DocumentStatus
from services.stock_service import StockService

class OperationService:
    @staticmethod
    @transaction.atomic
    def validate_operation(operation_id, user=None):
        """
        Validates an operation and triggers the corresponding stock movements.
        """
        operation = Operation.objects.select_for_update().get(pk=operation_id)

        if operation.status != DocumentStatus.DRAFT and operation.status != DocumentStatus.WAITING:
             # Allow re-validation if needed or handle strict state transitions
             # For now, assume we only validate from Draft/Waiting
             if operation.status == DocumentStatus.DONE:
                 raise ValueError("Operation is already done")

        lines = operation.lines.all()
        
        if not lines.exists():
            raise ValueError("Cannot validate an empty operation")

        if operation.operation_type == Operation.Type.RECEIPT:
            # Incoming: Supplier -> Destination Location (usually a default receiving area or specified per line if we had that, but here we use operation logic)
            # Assuming Receipt has a destination_location or we pick a default. 
            # The model has destination_location.
            if not operation.destination_location:
                raise ValueError("Destination location required for Receipt")
            
            for line in lines:
                StockService.increase_stock(
                    product=line.product,
                    location=operation.destination_location,
                    quantity=line.quantity_demanded,
                    operation=operation,
                    user=user
                )
                line.quantity_done = line.quantity_demanded
                line.save()

        elif operation.operation_type == Operation.Type.DELIVERY:
            # Outgoing: Source Location -> Customer
            if not operation.source_location:
                raise ValueError("Source location required for Delivery")

            for line in lines:
                StockService.decrease_stock(
                    product=line.product,
                    location=operation.source_location,
                    quantity=line.quantity_demanded,
                    operation=operation,
                    user=user
                )
                line.quantity_done = line.quantity_demanded
                line.save()

        elif operation.operation_type == Operation.Type.TRANSFER:
            # Internal: Source -> Destination
            if not operation.source_location or not operation.destination_location:
                raise ValueError("Source and Destination locations required for Transfer")

            for line in lines:
                StockService.move_stock(
                    product=line.product,
                    from_loc=operation.source_location,
                    to_loc=operation.destination_location,
                    quantity=line.quantity_demanded,
                    operation=operation,
                    user=user
                )
                line.quantity_done = line.quantity_demanded
                line.save()

        elif operation.operation_type == Operation.Type.ADJUSTMENT:
            # Adjustment: Set stock to specific quantity
            # Adjustment usually specifies a location.
            # If the operation has a source_location, we assume that's where we are adjusting.
            if not operation.source_location:
                 raise ValueError("Location required for Adjustment")
            
            for line in lines:
                StockService.adjust_stock(
                    product=line.product,
                    location=operation.source_location,
                    new_quantity=line.quantity_demanded, # In adjustment, demanded = counted
                    operation=operation,
                    user=user
                )
                line.quantity_done = line.quantity_demanded
                line.save()

        operation.status = DocumentStatus.DONE
        operation.validated_at = timezone.now()
        operation.save()
        return operation
