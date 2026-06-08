from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Shop, Category, Product, ProductInfo
from orders.models import Cart, Contact, Order, OrderItem



User = get_user_model()

class CartTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='cartuser@example.com', username='cartuser', password='testpass')
        cls.shop = Shop.objects.create(name='Тестовый магазин')
        cls.category = Category.objects.create(name='Телефоны')
        cls.product = Product.objects.create(name='iPhone 15', category=cls.category)
        cls.product_info = ProductInfo.objects.create(
            product=cls.product,
            shop=cls.shop,
            quantity=10,
            price=99990,
            external_id=123,
            model='A2846'
        )

        cls.cart_url = reverse('cart')
        cls.add_to_cart_url = reverse('add-to-cart')


    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_add_to_cart(self):
        """Добавление товара в корзину"""
        data = {'product_info_id': self.product_info.id, 'quantity': 2}
        response = self.client.post(self.add_to_cart_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertIn('item_id', response.data)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        cart_item = cart.items.first()
        self.assertEqual(cart_item.product_info, self.product_info)
        self.assertEqual(cart_item.quantity, 2)

    def test_add_to_cart_invalid_product(self):
        """Добавление несуществующего товара"""
        data = {'product_info_id': 9999, 'quantity': 1}
        response = self.client.post(self.add_to_cart_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_view_cart(self):
        """Просмотр корзины"""
        self.client.post(self.add_to_cart_url, {'product_info_id': self.product_info.id, 'quantity': 1})
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        item = response.data['items'][0]
        self.assertEqual(item['product_name'], 'iPhone 15')
        self.assertEqual(item['quantity'], 1)
        self.assertEqual(item['total'], 99990)

    def test_remove_from_cart(self):
        """Удаление товара из корзины"""
        post_response = self.client.post(self.add_to_cart_url, {'product_info_id': self.product_info.id, 'quantity': 1})
        item_id = post_response.data['item_id']
        remove_url = reverse('remove-from-cart', args=[item_id])
        response = self.client.delete(remove_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 0)

    def test_remove_from_cart_invalid_item(self):
        """Удаление несуществующего товара из корзины"""
        remove_url = reverse('remove-from-cart', args=[9999])
        response = self.client.delete(remove_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_cart_unauthorized(self):
        """Неавторизованный пользователь не может работать с корзиной"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ContactOrderTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='contactorder@example.com', username='contactuser', password='testpass')
        cls.shop = Shop.objects.create(name='Тестовый магазин')
        cls.category = Category.objects.create(name='Электроника')
        cls.product = Product.objects.create(name='Ноутбук', category=cls.category)
        cls.product_info = ProductInfo.objects.create(
            product=cls.product,
            shop=cls.shop,
            quantity=5,
            price=50000,
            external_id=456,
            model='X123'
        )
        cls.contacts_url = reverse('contacts')
        cls.confirm_order_url = reverse('confirm-order')
        cls.orders_url = reverse('orders')
        cls.add_to_cart_url = reverse('add-to-cart')

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_create_contact(self):
        """Создание контакта (адрес доставки)"""
        data = {
            'city': 'Москва',
            'street': 'Тверская',
            'house': '10',
            'phone': '+7 999 123-45-67'
        }
        response = self.client.post(self.contacts_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['city'], 'Москва')
        self.assertEqual(response.data['street'], 'Тверская')
        self.assertEqual(response.data['house'], '10')
        self.assertEqual(response.data['phone'], '+7 999 123-45-67')
        self.assertEqual(Contact.objects.count(), 1)

    def test_list_contacts(self):
        """Получение списка контактов"""
        Contact.objects.create(user=self.user, city='СПб', street='Невский', house='1', phone='123')
        response = self.client.get(self.contacts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['city'], 'СПб')

    def test_delete_contact(self):
        """Удаление контакта"""
        contact = Contact.objects.create(user=self.user, city='Казань', street='Баумана', house='5', phone='456')
        url = reverse('contact-delete', args=[contact.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Contact.objects.count(), 0)

    def test_confirm_order_success(self):
        """Успешное подтверждение заказа"""
        self.client.post(self.add_to_cart_url, {'product_info_id': self.product_info.id, 'quantity': 2})
        contact = Contact.objects.create(user=self.user, city='Москва', street='Тверская', house='10', phone='123')
        # Подтверждаем заказ
        data = {'contact_id': contact.id}
        response = self.client.post(self.confirm_order_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'confirmed')
        self.assertIn('order_id', response.data)
        order_id = response.data['order_id']
        # Проверяем, что заказ создался
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.contact, contact)
        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.product_info, self.product_info)
        self.assertEqual(order_item.quantity, 2)
        # Проверяем, что корзина очищена
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 0)
        # Проверяем отправку email (письмо покупателю и администратору)
        self.assertEqual(len(mail.outbox), 2)  # два письма
        self.assertIn('Заказ оформлен', mail.outbox[0].subject)
        self.assertIn(str(order_id), mail.outbox[0].body)
        self.assertIn('Новый заказ', mail.outbox[1].subject)

    def test_confirm_order_empty_cart(self):
        """Подтверждение заказа с пустой корзиной"""
        contact = Contact.objects.create(user=self.user, city='Москва', street='Тверская', house='10', phone='123')
        data = {'contact_id': contact.id}
        response = self.client.post(self.confirm_order_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_confirm_order_invalid_contact(self):
        """Подтверждение заказа с несуществующим контактом"""
        data = {'contact_id': 9999}
        response = self.client.post(self.confirm_order_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_order_list(self):
        """Получение списка заказов пользователя"""
        contact = Contact.objects.create(user=self.user, city='Москва', street='Тверская', house='10', phone='123')
        order = Order.objects.create(user=self.user, status='new', contact=contact)
        OrderItem.objects.create(order=order, product_info=self.product_info, quantity=1)
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order.id)
        self.assertEqual(response.data[0]['status'], 'new')
        self.assertEqual(len(response.data[0]['items']), 1)
        self.assertEqual(response.data[0]['items'][0]['product_name'], 'Ноутбук')

    def test_order_detail(self):
        """Детали заказа"""
        contact = Contact.objects.create(user=self.user, city='Москва', street='Тверская', house='10', phone='123')
        order = Order.objects.create(user=self.user, status='new', contact=contact)
        OrderItem.objects.create(order=order, product_info=self.product_info, quantity=2)
        url = reverse('order-detail', args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)
        self.assertEqual(response.data['total_amount'], '100000.00')  # 2 * 50000
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['quantity'], 2)