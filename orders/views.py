from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Cart, CartItem, Contact, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, ContactSerializer, OrderConfirmSerializer, OrderSerializer, OrderStatusUpdateSerializer
from products.models import ProductInfo
from main.tasks import send_email_task
from django.conf import settings


class CartView(generics.RetrieveAPIView):
    """Просмотр корзины"""
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(generics.CreateAPIView):
    """Добавление товара в корзину"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_info_id = request.data.get('product_info_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product_info = ProductInfo.objects.get(id=product_info_id)
        except ProductInfo.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_info=product_info,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({'status': 'ok', 'item_id': cart_item.id})


class RemoveFromCartView(generics.DestroyAPIView):
    """Удаление товара из корзины"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            return Response({'status': 'ok'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Товар не найден в корзине'}, status=status.HTTP_404_NOT_FOUND)
        

class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ContactDestroyView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)
    

class ConfirmOrderView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_id = serializer.validated_data['contact_id']

        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response({'error': 'Контакт не найден'}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, status='new', contact=contact)

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_info=cart_item.product_info,
                quantity=cart_item.quantity
            )

        cart.items.all().delete()

        send_email_task.delay(
            subject='Заказ оформлен',
            message=f'Ваш заказ №{order.id} принят. Сумма: {order.total_amount}',
            recipient_list=[request.user.email]
        )

        send_email_task.delay(
            subject='Новый заказ',
            message=f'Поступил заказ №{order.id} от {request.user.email} на сумму {order.total_amount} руб.',
            recipient_list=['admin@example.com']
        )

        return Response({'order_id': order.id, 'status': 'confirmed'})
    

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product_info__product', 'items__product_info__shop')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product_info__product', 'items__product_info__shop')
    

class OrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'shop') and user.shop:
            return Order.objects.filter(items__shop=user.shop).distinct()
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.none()
    
    def perform_update(self, serializer):
        order = serializer.save()
        send_email_task.delay(
            subject=f'Статус заказа №{order.id} изменён',
            message=f'Ваш заказ №{order.id} теперь имеет статус: {order.get_status_display()}.',
            recipient_list=[order.user.email]
        )