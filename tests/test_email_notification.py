from django.test import TestCase
from unittest.mock import patch
from inventory.models import Product, Warehouse, Location, Category, Operation, OperationLine
from services.operation_service import OperationService
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailNotificationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='manager', password='password', role='MANAGER')
        self.warehouse = Warehouse.objects.create(name="Test Warehouse")
        self.loc1 = Location.objects.create(name="Loc 1", warehouse=self.warehouse, code="L1")
        self.loc2 = Location.objects.create(name="Loc 2", warehouse=self.warehouse, code="L2")
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", sku="TEST", category=self.category)
        
        # Create initial stock in Loc 1
        # Create dummy receipt to add stock
        op_receipt = Operation.objects.create(operation_type=Operation.Type.RECEIPT, destination_location=self.loc1)
        OperationLine.objects.create(operation=op_receipt, product=self.product, quantity_demanded=100)
        OperationService.validate_operation(op_receipt.id, self.user)

    @patch('services.notification_service.send_mail')
    def test_transfer_email(self, mock_send_mail):
        # Create Transfer
        op = Operation.objects.create(
            operation_type=Operation.Type.TRANSFER,
            source_location=self.loc1,
            destination_location=self.loc2,
            created_by=self.user
        )
        OperationLine.objects.create(operation=op, product=self.product, quantity_demanded=10)
        
        # Validate
        OperationService.validate_operation(op.id, self.user)
        
        # Check if send_mail was called
        self.assertTrue(mock_send_mail.called)
        args, kwargs = mock_send_mail.call_args
        self.assertIn("Transfer Validated", kwargs['subject'])
        self.assertIn("Loc 1", kwargs['message'])
        self.assertIn("Loc 2", kwargs['message'])
        self.assertIn("TEST", kwargs['message'])
