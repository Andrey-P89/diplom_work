from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

User = get_user_model()

class ProductListTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.shop = Shop.objects.create(name='Тестовый магазин', state=True)
        cls.category = Category.objects.create(name='Телефоны')
        cls.product = Product.objects.create(name='iPhone 15', category=cls.category, description='Новый iPhone')
        cls.product_info = ProductInfo.objects.create(
            product=cls.product,
            shop=cls.shop,
            quantity=10,
            price=99990,
            external_id=123,
            model='A2846'
        )

        cls.param = Parameter.objects.create(name='Цвет')
        ProductParameter.objects.create(
            product_info=cls.product_info,
            parameter=cls.param,
            value='черный'
        )

        cls.url = reverse('products')

    def test_list_products_public(self):
        """Список товаров доступен без токена"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_filter_by_shop(self):
        """Фильтрация по shop__name"""
        response = self.client.get(self.url, {'shop__name': 'Тестовый магазин'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что вернулся товар с нужным поставщиком
        self.assertTrue(any(item['supplier'] == 'Тестовый магазин' for item in response.data))

    def test_search_by_product_name(self):
        """Поиск по названию товара (search)"""
        response = self.client.get(self.url, {'search': 'iPhone'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any('iPhone' in item['name'] for item in response.data))