from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from inventory.models import Product, Warehouse, Location, Category, ProductStock, StockMovement, Operation
from django.utils import timezone

User = get_user_model()

class DashboardChartsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password', role='MANAGER')
        self.client.force_authenticate(user=self.user)

        self.warehouse = Warehouse.objects.create(name="Test Warehouse")
        self.location = Location.objects.create(name="Test Location", warehouse=self.warehouse, code="LOC-001")
        self.category1 = Category.objects.create(name="Cat 1")
        self.category2 = Category.objects.create(name="Cat 2")
        
        self.p1 = Product.objects.create(name="P1", sku="SKU1", category=self.category1)
        self.p2 = Product.objects.create(name="P2", sku="SKU2", category=self.category2)
        
        # Create stock
        ProductStock.objects.create(product=self.p1, location=self.location, quantity=10)
        ProductStock.objects.create(product=self.p2, location=self.location, quantity=20)
        
        # Create movements
        StockMovement.objects.create(
            product=self.p1, quantity=5, transaction_type=Operation.Type.RECEIPT,
            timestamp=timezone.now()
        )
        StockMovement.objects.create(
            product=self.p2, quantity=15, transaction_type=Operation.Type.RECEIPT,
            timestamp=timezone.now()
        )

    def test_charts_api(self):
        response = self.client.get('/api/dashboard/charts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check Stock by Category
        stock_data = response.data['stock_by_category']
        self.assertEqual(len(stock_data), 2)
        # Cat 2 has 20, Cat 1 has 10. Order is desc.
        self.assertEqual(stock_data[0]['category__name'], 'Cat 2')
        self.assertEqual(stock_data[0]['total_qty'], 20)
        
        # Check Top Movers
        movers_data = response.data['top_movers']
        self.assertEqual(len(movers_data), 2)
        # P2 moved 15, P1 moved 5. Order desc.
        self.assertEqual(movers_data[0]['product__name'], 'P2')
        self.assertEqual(movers_data[0]['total_qty'], 15)
