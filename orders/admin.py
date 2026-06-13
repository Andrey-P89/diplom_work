from django.contrib import admin
from .models import Contact, Order, OrderItem, Cart, CartItem

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'city', 'street', 'house', 'phone')
    search_fields = ('user__email', 'city', 'street')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dt', 'status', 'contact')
    list_filter = ('status',)
    search_fields = ('user__email',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_info', 'quantity')
    search_fields = ('order__id',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product_info', 'quantity')