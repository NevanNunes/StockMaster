from django.test import TestCase
from django.contrib.auth import get_user_model
from inventory.models import Warehouse, Location, Product, Operation, DocumentStatus, ProductStock, StockMovement
from services.stock_service import StockService
from services.operation_service import OperationService

User = get_user_model()

class StockFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.warehouse = Warehouse.objects.create(name='Test WH', code='WH-TEST')
        self.loc_recv = Location.objects.create(warehouse=self.warehouse, name='Receiving', code='RECV')
        self.loc_storage = Location.objects.create(warehouse=self.warehouse, name='Storage', code='STORE')
        self.product = Product.objects.create(name='Test Product', sku='TEST-001', uom='pcs')

    def test_receipt_flow(self):
        # 1. Create Receipt
        op = Operation.objects.create(
            operation_type=Operation.Type.RECEIPT,
            destination_location=self.loc_recv,
            created_by=self.user,
            status=DocumentStatus.DRAFT
        )
        op.lines.create(product=self.product, quantity_demanded=100)

        # 2. Validate
        OperationService.validate_operation(op.id, self.user)

        # 3. Check Stock
        stock = ProductStock.objects.get(product=self.product, location=self.loc_recv)
        self.assertEqual(stock.quantity, 100)

        # 4. Check Ledger
        move = StockMovement.objects.last()
        self.assertEqual(move.quantity, 100)
        self.assertEqual(move.to_location, self.loc_recv)
        self.assertEqual(move.transaction_type, Operation.Type.RECEIPT)

    def test_transfer_flow(self):
        # Setup initial stock
        StockService.increase_stock(self.product, self.loc_recv, 100, Operation.objects.create(operation_type='ADJUSTMENT'), self.user)

        # 1. Create Transfer
        op = Operation.objects.create(
            operation_type=Operation.Type.TRANSFER,
            source_location=self.loc_recv,
            destination_location=self.loc_storage,
            created_by=self.user,
            status=DocumentStatus.DRAFT
        )
        op.lines.create(product=self.product, quantity_demanded=50)

        # 2. Validate
        OperationService.validate_operation(op.id, self.user)

        # 3. Check Stock
        stock_recv = ProductStock.objects.get(product=self.product, location=self.loc_recv)
        stock_store = ProductStock.objects.get(product=self.product, location=self.loc_storage)
        
        self.assertEqual(stock_recv.quantity, 50)
        self.assertEqual(stock_store.quantity, 50)

    def test_insufficient_stock(self):
        # 1. Create Delivery without stock
        op = Operation.objects.create(
            operation_type=Operation.Type.DELIVERY,
            source_location=self.loc_storage,
            created_by=self.user,
            status=DocumentStatus.DRAFT
        )
        op.lines.create(product=self.product, quantity_demanded=10)

        # 2. Validate should fail
        with self.assertRaises(ValueError):
            OperationService.validate_operation(op.id, self.user)
