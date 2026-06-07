from rest_framework import serializers
from .models import Cart, CartItem, Contact, OrderItem, Order
from products.models import ProductInfo


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_info.product.name')
    shop_name = serializers.CharField(source='product_info.shop.name')
    price = serializers.DecimalField(source='product_info.price', max_digits=12, decimal_places=2)
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product_info', 'product_name', 'shop_name', 'price', 'quantity', 'total']

    def get_total(self, obj):
        return obj.quantity * obj.product_info.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    def get_total_price(self, obj):
        return sum(item.quantity * item.product_info.price for item in obj.items.all())


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'type', 'user', 'value']
        read_only_fields = ['user']


class OrderConfirmSerializer(serializers.Serializer):
    contact_id = serializers.IntegerField()


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    shop_name = serializers.CharField(source='shop.name')
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'shop_name', 'quantity', 'total']

    def get_total(self, obj):
        product_info = obj.product.product_infos.filter(shop=obj.shop).first()
        price = product_info.price if product_info else 0
        return price * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'dt', 'status', 'total_amount', 'items']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']