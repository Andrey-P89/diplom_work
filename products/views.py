from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductInfo
from .serializers import ProductInfoListSerializer

class ProductListView(generics.ListAPIView):
    """
    Список товаров с возможностью фильтрации и поиска.

    GET-запрос возвращает все товары (с учетом наличия в магазинах).
    Параметры фильтрации (через query string):
    - `?shop__name=...` – фильтр по названию магазина
    - `?product__category__name=...` – фильтр по категории товара
    Поиск (через `?search=...`) осуществляется по полям названия товара и его описания.

    Поле `parameters` содержит список характеристик товара в формате [{"name": "...", "value": "..."}].
    """
    queryset = ProductInfo.objects.select_related('product', 'shop').prefetch_related('parameters__parameter')
    serializer_class = ProductInfoListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['shop__name', 'product__category__name']
    search_fields = ['product__name', 'product__description']


class ProductDetailView(generics.RetrieveAPIView):
    """
    Детальная информация о конкретном товаре в определённом магазине.

    GET-запрос с указанием pk (идентификатора ProductInfo) в URL.
    Возвращает те же поля, что и список товаров, но только для одной записи.
    """
    queryset = ProductInfo.objects.select_related('product', 'shop').prefetch_related('parameters__parameter')
    serializer_class = ProductInfoListSerializer
    lookup_field = 'pk'