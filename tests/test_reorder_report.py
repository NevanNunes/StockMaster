from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from inventory.models import Product, Warehouse, Location, Category, ProductStock

User = get_user_model()

class ReorderReportTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password', role='MANAGER')
        self.client.force_authenticate(user=self.user)

        self.warehouse = Warehouse.objects.create(name="Test Warehouse")
        self.location = Location.objects.create(name="Test Location", warehouse=self.warehouse, code="LOC-001")
        self.category = Category.objects.create(name="Test Category")
        
        # Product 1: Low Stock (5 < 10)
        self.p1 = Product.objects.create(name="P1", sku="SKU1", category=self.category, min_stock_level=10)
        ProductStock.objects.create(product=self.p1, location=self.location, quantity=5)
        
        # Product 2: Adequate Stock (15 > 10)
        self.p2 = Product.objects.create(name="P2", sku="SKU2", category=self.category, min_stock_level=10)
        ProductStock.objects.create(product=self.p2, location=self.location, quantity=15)
        
        # Product 3: No Stock (0 < 10)
        self.p3 = Product.objects.create(name="P3", sku="SKU3", category=self.category, min_stock_level=10)

    def test_reorder_report_api(self):
        response = self.client.get('/api/inventory/reorder-report/')
        print(f"Response Data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should contain P1 and P3, but not P2
        skus = [p['sku'] for p in response.data]
        self.assertIn('SKU1', skus)
        self.assertIn('SKU3', skus)
        self.assertNotIn('SKU2', skus)
        
        # Check total_stock values
        p1_data = next(p for p in response.data if p['sku'] == 'SKU1')
        self.assertEqual(p1_data['total_stock'], 5)
        
        p3_data = next(p for p in response.data if p['sku'] == 'SKU3')
        self.assertEqual(p3_data['total_stock'], 0)
