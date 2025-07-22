from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Investor

User = get_user_model()

class InvestorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', role='Investor')
        self.client.force_authenticate(user=self.user)

    def test_create_investor(self):
        url = reverse('investor-list-create')
        data = {
            'contact': 'test contact',
            'join_date': '2023-01-01',
            'total_investment': '10000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_investors(self):
        Investor.objects.create(user=self.user, contact='contact', join_date='2023-01-01', total_investment=5000)
        url = reverse('investor-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_investor(self):
        investor = Investor.objects.create(user=self.user, contact='contact', join_date='2023-01-01', total_investment=5000)
        url = reverse('investor-detail', kwargs={'pk': investor.id})
        data = {
            'contact': 'updated contact',
            'join_date': '2023-01-01',
            'total_investment': '15000.00'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_investor(self):
        investor = Investor.objects.create(user=self.user, contact='contact', join_date='2023-01-01', total_investment=5000)
        url = reverse('investor-detail', kwargs={'pk': investor.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

