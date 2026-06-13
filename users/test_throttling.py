from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.test import override_settings

class ThrottlingTest(APITestCase):
    @override_settings(REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle'],
        'DEFAULT_THROTTLE_RATES': {'anon': '10/minute'},
    })
    def test_anon_throttle_products(self):
        url = reverse('products')  # имя маршрута для списка товаров
        # Делаем 11 быстрых GET-запросов
        for i in range(11):
            response = self.client.get(url)
            if i < 10:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)