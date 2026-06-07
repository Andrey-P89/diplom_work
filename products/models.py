from django.db import models
    

class Shop(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(blank=True, verbose_name='Ссылка для импорта')
    user = models.OneToOneField(
        'users.User', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        verbose_name='Пользователь'
        )
    state = models.BooleanField(default=True, verbose_name='Статус получения заказов')

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=50)
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.name
    

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_infos')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_infos')
    name = models.CharField(max_length=200, verbose_name='Название в магазине')
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_rrc = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    model = models.CharField(max_length=80, blank=True, verbose_name='Модель')
    
    class Meta:
        unique_together = ['product', 'shop', 'external_id']
    
    def __str__(self):
        return f"{self.product.name} - {self.shop.name}: {self.price} руб."
    

class Parameter(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='parameters')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    value = models.CharField(max_length=300)
    
    class Meta:
        unique_together = ['product_info', 'parameter']
    
    def __str__(self):
        return f"{self.parameter.name}: {self.value}"