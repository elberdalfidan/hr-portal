from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

class UserAuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_login_url = reverse('accounts:admin_login_api')
        self.staff_login_url = reverse('accounts:staff_login_api')
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@admin.com',
            password='1',
            is_staff=True,
            is_superuser=True
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@staff.com',
            password='1',
            is_staff=True,
        )

    def test_admin_user_login_success(self):
        response = self.client.post(self.admin_login_url, {
            'username': 'admin',
            'password': '1'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_staff_user_login_success(self):
        response = self.client.post(self.staff_login_url, {
            'username': 'staff',
            'password': '1'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('_auth_user_id' in self.client.session) 

    def test_admin_user_login_with_wrong_credentials(self):
        response = self.client.post(self.admin_login_url, {
            'username': 'admin',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_user_login_with_wrong_credentials(self):
        response = self.client.post(self.staff_login_url, {
            'username': 'staff',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
