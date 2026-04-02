from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import EnergyUsage
import datetime

User = get_user_model()

class EnergyUsageAPITests(APITestCase):
    def setUp(self):
        # Admins
        self.admin_user = User.objects.create_user(username='admin', password='password', role='ADMIN')
        
        # Staff
        self.staff_user = User.objects.create_user(username='staff', password='password', role='STAFF')
        
        # Single record
        self.energy = EnergyUsage.objects.create(
            building_name='Main Lab',
            units_consumed=150.0,
            month=datetime.date(2023, 1, 1),
            created_by=self.admin_user
        )
        
        self.url = '/api/energy/'
        self.detail_url = f'/api/energy/{self.energy.id}/'

    def test_get_endpoints_unauthenticated(self):
        # Verification that JWT/Auth is REQUIRED
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response_post = self.client.post(self.url, {})
        self.assertEqual(response_post.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_and_get_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        
        # Test GET
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test POST
        data = {
            'building_name': 'Block B',
            'units_consumed': 50.0,
            'month': '2023-02-01'
        }
        res_post = self.client.post(self.url, data)
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EnergyUsage.objects.count(), 2)

    def test_put_and_delete_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        
        # Test PUT (should be forbidden)
        data = {'building_name': 'Updated Name', 'units_consumed': 200.0, 'month': '2023-01-01'}
        res_put = self.client.put(self.detail_url, data)
        self.assertEqual(res_put.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test DELETE (should be forbidden)
        res_del = self.client.delete(self.detail_url)
        self.assertEqual(res_del.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_and_delete_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        
        # Test PUT (Allowed for Admin)
        data = {'building_name': 'Updated Name', 'units_consumed': 200.0, 'month': '2023-01-01'}
        res_put = self.client.put(self.detail_url, data)
        self.assertEqual(res_put.status_code, status.HTTP_200_OK)
        
        # Test DELETE (Allowed for Admin)
        res_del = self.client.delete(self.detail_url)
        self.assertEqual(res_del.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EnergyUsage.objects.count(), 0)
