from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductInfo
from .serializers import ProductInfoListSerializer

class ProductListView(generics.ListAPIView):
    queryset = ProductInfo.objects.select_related('product', 'shop').prefetch_related('parameters__parameter')
    serializer_class = ProductInfoListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['shop__name', 'product__category__name']
    search_fields = ['product__name', 'product__description']


class ProductDetailView(generics.RetrieveAPIView):
    queryset = ProductInfo.objects.select_related('product', 'shop').prefetch_related('parameters__parameter')
    serializer_class = ProductInfoListSerializer
    lookup_field = 'pk'