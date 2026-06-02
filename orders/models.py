from django.db import models

from django.contrib.auth import get_user_model
from products.models import Product, Shop

User = get_user_model()


class Order(models.Model):
    """Заказ"""
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    def __str__(self):
        return f"Заказ №{self.id} - {self.user.email} ({self.status})"


class OrderItem(models.Model):
    """Товар в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity} - {self.shop.name}"


class Contact(models.Model):
    CONTACT_TYPES = (
        ('phone', 'Телефон'),
        ('address', 'Адрес'),
    )
    
    type = models.CharField(max_length=10, choices=CONTACT_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    value = models.TextField()
    
    def __str__(self):
        return f"{self.user.email} - {self.type}: {self.value}"