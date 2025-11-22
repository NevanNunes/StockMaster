from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from inventory.models import Product, Warehouse, Location, Category, LowStockAlert, ProductStock
from services.stock_service import StockService
from inventory.models import Operation

User = get_user_model()

class LowStockAlertsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password', role='MANAGER')
        self.client.force_authenticate(user=self.user)

        self.warehouse = Warehouse.objects.create(name="Test Warehouse")
        self.location = Location.objects.create(name="Test Location", warehouse=self.warehouse, code="LOC-001")
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST-SKU",
            category=self.category,
            min_stock_level=10
        )
        
        # Create initial stock
        self.stock = ProductStock.objects.create(product=self.product, location=self.location, quantity=20)
        
        # Create dummy operation for stock movement
        self.operation = Operation.objects.create(
            operation_type=Operation.Type.DELIVERY,
            created_by=self.user,
            source_location=self.location
        )

    def test_alert_creation_and_api(self):
        # Decrease stock to trigger alert (20 -> 5)
        StockService.decrease_stock(
            product=self.product,
            location=self.location,
            quantity=15,
            operation=self.operation,
            user=self.user
        )
        
        # Check if alert exists in DB
        self.assertTrue(LowStockAlert.objects.filter(product=self.product, is_resolved=False).exists())
        
        # Check API list
        response = self.client.get('/api/inventory/alerts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        alert_id = response.data[0]['id']
        
        # Check unread count
        response = self.client.get('/api/inventory/alerts/unread_count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Mark as read
        response = self.client.post(f'/api/inventory/alerts/{alert_id}/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check unread count again
        response = self.client.get('/api/inventory/alerts/unread_count/')
        self.assertEqual(response.data['count'], 0)
        
        # Check list again (should still be there as it's not resolved, just read)
        response = self.client.get('/api/inventory/alerts/')
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['is_read'])

