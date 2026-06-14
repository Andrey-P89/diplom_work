from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.throttling import AnonRateThrottle


class ThrottlingTest(APITestCase):
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = reverse('products')

    def test_anon_throttle_products(self):
        # 1. Создаем запрос
        request = self.factory.get(self.url)
        
        # 2. Имитируем анонимного пользователя и задаем IP
        request.user = None
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # 3. Создаем экземпляр троттлинга
        throttle = AnonRateThrottle()
        
        # 4. ВАЖНО: Явно включаем троттлинг и задаем лимит, 
        # чтобы перебить None, который подставился из-за отключения в settings.py
        throttle.rate = '2/second'
        throttle.num_requests, throttle.duration = throttle.parse_rate(throttle.rate)
        
        # 5. Проверяем логику
        # 1-й запрос: должен пройти
        self.assertTrue(throttle.allow_request(request, view=None))
        
        # 2-й запрос: должен пройти
        self.assertTrue(throttle.allow_request(request, view=None))
        
        # 3-й запрос: должен быть заблокирован (вернет False)
        self.assertFalse(throttle.allow_request(request, view=None))