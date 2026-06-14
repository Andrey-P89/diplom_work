from rest_framework import serializers
from .models import ProductInfo, ProductParameter

class ProductParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='parameter.name')
    class Meta:
        model = ProductParameter
        fields = ['name', 'value']

class ProductInfoListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product.name')
    description = serializers.CharField(source='product.description')
    supplier = serializers.CharField(source='shop.name')
    parameters = ProductParameterSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductInfo
        fields = ['id', 'name', 'description', 'supplier', 'price', 'quantity', 'parameters', 'image_url']

    def get_image_url(self, obj):
        if obj.product.image:
            return obj.product.image.url
        return None