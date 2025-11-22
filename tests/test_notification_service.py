from django.test import TestCase
from django.core import mail
from inventory.models import Product, Category, Warehouse, Location
from services.notification_service import NotificationService
from decimal import Decimal


class NotificationServiceTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.warehouse = Warehouse.objects.create(name="Main", code="MAIN")
        self.location = Location.objects.create(
            warehouse=self.warehouse,
            name="Rack A",
            code="A1"
        )
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST-001",
            category=self.category,
            uom="pcs",
            min_stock_level=10
        )
    
    def test_email_sent_when_below_minimum(self):
        """Test that email is sent when stock is below minimum"""
        NotificationService.notify_low_stock(
            self.product,
            self.location,
            Decimal('5')  # Below min_stock_level of 10
        )
        
        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('Low Stock Alert', email.subject)
        self.assertIn('TEST-001', email.subject)
        self.assertIn('Test Product', email.body)
        self.assertIn('Rack A', email.body)
        self.assertIn('5', email.body)
    
    def test_no_email_when_above_minimum(self):
        """Test that NO email is sent when stock is above minimum"""
        NotificationService.notify_low_stock(
            self.product,
            self.location,
            Decimal('15')  # Above min_stock_level of 10
        )
        
        # Check that NO email was sent
        self.assertEqual(len(mail.outbox), 0)
