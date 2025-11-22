from django.test import TestCase
from django.contrib.auth import get_user_model
from inventory.models import Warehouse, Location, Product, Operation, DocumentStatus, ProductStock, StockMovement, LowStockAlert
from services.stock_service import StockService
from services.operation_service import OperationService
from decimal import Decimal

User = get_user_model()

class EnhancedServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.warehouse = Warehouse.objects.create(name='Test WH', code='WH-TEST')
        self.loc_recv = Location.objects.create(warehouse=self.warehouse, name='Receiving', code='RECV')
        self.loc_storage = Location.objects.create(warehouse=self.warehouse, name='Storage', code='STORE')
        self.product = Product.objects.create(name='Test Product', sku='TEST-001', uom='pcs', min_stock_level=10)

    def test_low_stock_alert_creation(self):
        # 1. Increase stock to 20 (above min 10)
        op = Operation.objects.create(operation_type=Operation.Type.RECEIPT)
        StockService.increase_stock(self.product, self.loc_storage, Decimal('20'), op)
        
        self.assertFalse(LowStockAlert.objects.filter(product=self.product, is_resolved=False).exists())

        # 2. Decrease stock to 5 (below min 10)
        op_del = Operation.objects.create(operation_type=Operation.Type.DELIVERY)
        StockService.decrease_stock(self.product, self.loc_storage, Decimal('15'), op_del)

        # Check alert created
        alert = LowStockAlert.objects.get(product=self.product, location=self.loc_storage, is_resolved=False)
        self.assertEqual(alert.current_quantity, 5)
        self.assertEqual(alert.threshold, 10)

    def test_low_stock_alert_resolution(self):
        # Setup: Create alert
        op = Operation.objects.create(operation_type=Operation.Type.RECEIPT)
        StockService.increase_stock(self.product, self.loc_storage, Decimal('5'), op)
        # Manually trigger alert check if needed, but increase_stock doesn't create alerts, only resolves.
        # So let's use adjust to set low stock first.
        StockService.adjust_stock(self.product, self.loc_storage, Decimal('5'), op)
        self.assertTrue(LowStockAlert.objects.filter(product=self.product, is_resolved=False).exists())

        # 1. Increase stock to 15 (above min 10)
        StockService.increase_stock(self.product, self.loc_storage, Decimal('10'), op)

        # Check alert resolved
        self.assertFalse(LowStockAlert.objects.filter(product=self.product, is_resolved=False).exists())
        resolved_alert = LowStockAlert.objects.get(product=self.product, is_resolved=True)
        self.assertIsNotNone(resolved_alert.resolved_at)

    def test_partial_validation(self):
        # Setup: 10 units in stock
        op_rec = Operation.objects.create(operation_type=Operation.Type.RECEIPT, destination_location=self.loc_storage)
        StockService.increase_stock(self.product, self.loc_storage, Decimal('10'), op_rec)

        # 1. Create Delivery for 20 units
        op = Operation.objects.create(
            operation_type=Operation.Type.DELIVERY,
            source_location=self.loc_storage,
            status=DocumentStatus.DRAFT
        )
        op.lines.create(product=self.product, quantity_demanded=20)

        # 2. Validate with allow_partial=True
        OperationService.validate_operation(op.id, allow_partial=True)

        # 3. Check results
        op.refresh_from_db()
        line = op.lines.first()
        stock = ProductStock.objects.get(product=self.product, location=self.loc_storage)

        self.assertEqual(op.status, DocumentStatus.DONE)
        self.assertEqual(line.quantity_done, 10) # Only 10 available
        self.assertEqual(stock.quantity, 0)

    def test_ledger_enrichment(self):
        op = Operation.objects.create(operation_type=Operation.Type.RECEIPT)
        StockService.increase_stock(self.product, self.loc_storage, Decimal('50'), op, notes="Test Note")

        move = StockMovement.objects.last()
        self.assertEqual(move.balance_after, 50)
        self.assertEqual(move.notes, "Test Note")
