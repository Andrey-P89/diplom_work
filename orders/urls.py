from django.urls import path
from .views import CartView, AddToCartView, RemoveFromCartView, ContactListCreateView, ContactDestroyView, ConfirmOrderView, OrderListView, OrderDetailView, OrderStatusUpdateView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('contacts/', ContactListCreateView.as_view(), name='contacts'),
    path('contacts/<int:pk>/', ContactDestroyView.as_view(), name='contact-delete'),
    path('orders/confirm/', ConfirmOrderView.as_view(), name='confirm-order'),
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
]