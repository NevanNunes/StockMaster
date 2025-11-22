from django.test import TestCase
from rest_framework.test import APIClient
from inventory.models import Operation, DocumentStatus
from django.utils import timezone
from datetime import timedelta

class SearchFilteringTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create operations with different dates and names
        self.op1 = Operation.objects.create(
            operation_type=Operation.Type.RECEIPT,
            partner_name="Supplier A",
            reference_number="REC-001",
            created_at=timezone.now() - timedelta(days=10)
        )
        # Hack to set created_at manually (since auto_now_add overrides it on creation)
        Operation.objects.filter(id=self.op1.id).update(created_at=timezone.now() - timedelta(days=10))
        
        self.op2 = Operation.objects.create(
            operation_type=Operation.Type.DELIVERY,
            partner_name="Customer B",
            reference_number="DEL-001",
            created_at=timezone.now() - timedelta(days=2)
        )
        Operation.objects.filter(id=self.op2.id).update(created_at=timezone.now() - timedelta(days=2))

    def test_search_by_reference(self):
        response = self.client.get('/api/inventory/operations/?search=REC-001')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reference_number'], 'REC-001')

    def test_search_by_partner(self):
        response = self.client.get('/api/inventory/operations/?search=Customer B')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['partner_name'], 'Customer B')

    def test_filter_by_date_range(self):
        # Filter for last 5 days (should only find op2)
        start_date = (timezone.now() - timedelta(days=5)).date()
        response = self.client.get(f'/api/inventory/operations/?start_date={start_date}')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reference_number'], 'DEL-001')
