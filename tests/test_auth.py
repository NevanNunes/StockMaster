from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from inventory.models import Operation

User = get_user_model()

class AuthPermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create Manager
        self.manager = User.objects.create_user(
            username='manager', 
            password='password123',
            email='manager@test.com',
            role='MANAGER'
        )
        
        # Create Staff
        self.staff = User.objects.create_user(
            username='staff', 
            password='password123',
            email='staff@test.com',
            role='STAFF'
        )
        
        # Create Operation
        self.operation = Operation.objects.create(
            operation_type=Operation.Type.RECEIPT,
            partner_name="Test Supplier",
            reference_number="REC-AUTH-001",
            created_by=self.manager
        )

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access operations"""
        response = self.client.get('/api/inventory/operations/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_success(self):
        """Test login functionality"""
        response = self.client.post('/api/users/login/', {
            'username': 'manager',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'MANAGER')

    def test_manager_can_create_operation(self):
        """Test that managers can create operations"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post('/api/inventory/operations/', {
            'operation_type': 'RECEIPT',
            'partner_name': 'New Supplier',
            'status': 'DRAFT',
            'lines': []
        }, format='json')
        if response.status_code != 201:
            print(f"Create Operation Failed: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_cannot_validate_operation(self):
        """Test that staff cannot validate operations (custom permission)"""
        # Note: In a real scenario, validation is a custom action. 
        # Here we test if staff can update status to DONE directly via PATCH if that was the mechanism,
        # OR if we had a specific permission check on the validate endpoint.
        # Since IsManagerOrReadOnly allows write only to managers:
        
        self.client.force_authenticate(user=self.staff)
        response = self.client.patch(f'/api/inventory/operations/{self.operation.id}/', {
            'partner_name': 'Updated Supplier'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_update_operation(self):
        """Test that managers can update operations"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(f'/api/inventory/operations/{self.operation.id}/', {
            'partner_name': 'Updated Supplier'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
