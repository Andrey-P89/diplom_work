from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    """Тесты регистрации и авторизации (без дублирования)"""

    @classmethod
    def setUpTestData(cls):
        cls.register_url = reverse('register')
        cls.login_url = reverse('login')
        cls.valid_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'type': 'buyer'
        }

    def test_register_success(self):
        """Успешная регистрация"""
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['email'], self.valid_data['email'])
        self.assertEqual(User.objects.count(), 1)

    def test_register_password_mismatch(self):
        """Пароли не совпадают"""
        data = self.valid_data.copy()
        data['password_confirm'] = 'different'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_duplicate_email(self):
        """Email уже существует"""
        User.objects.create_user(email=self.valid_data['email'], username='existing', password='pass')
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_success(self):
        """Успешный логин"""
        self.client.post(self.register_url, self.valid_data)
        login_data = {
            'email': self.valid_data['email'],
            'password': self.valid_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['email'], self.valid_data['email'])

    def test_login_invalid_credentials(self):
        """Неверный пароль"""
        user = User.objects.create_user(email='bad@example.com', username='bad', password='correctpass')
        login_data = {
            'email': user.email,
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)