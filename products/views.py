from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend]

    filterset_fields = ['supplier']

    search_fields = ['name', 'description']