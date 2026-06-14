from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from django.core.cache import cache
from django.test import override_settings
from unittest.mock import patch

# 1. Создаем специальный класс троттлинга ТОЛЬКО для этого теста.
class TestAnonThrottle(AnonRateThrottle):
    rate = '2/second'

class ThrottlingTest(APITestCase):
    
    def setUp(self):
        self.url = reverse('products')

    # 2. Включаем кэш в памяти (чтобы не зависеть от Redis)
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    # 3. Мы подменяем throttle_classes у самого ProductListView.
    # DRF больше не сможет игнорировать троттлинг, так как мы подсовываем ему наш класс.
    @patch('products.views.ProductListView.throttle_classes', new=[TestAnonThrottle])
    def test_anon_throttle_products(self):
        # Очищаем кэш, чтобы начать счет с нуля
        cache.clear()
        
        # 1-й запрос: должен пройти (200 OK)
        response1 = self.client.get(self.url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # 2-й запрос: должен пройти (200 OK)
        response2 = self.client.get(self.url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # 3-й запрос: кэш "помнит" два запроса и блокирует этот (429)
        response3 = self.client.get(self.url)
        self.assertEqual(response3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)