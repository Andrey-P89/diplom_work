import yaml
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


def import_products(user_id, file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    shop_name = data.get('shop')

    shop, created = Shop.objects.get_or_create(user_id=user_id)

    if created:
        shop.name = shop_name
        shop.save()

    categories = {}
    for cat in data['categories']:
        category, _ = Category.objects.get_or_create(name=cat['name'])
        categories[cat['id']] = category
        category.shops.add(shop)
    
    for item in data['goods']:
        product, _ = Product.objects.get_or_create(
            name=item['name'],
            category=categories[item['category']]
        )
        
        product_info, _ = ProductInfo.objects.update_or_create(
            product=product,
            shop=shop,
            external_id=item['id'],
            defaults={
                'price': item['price'],
                'price_rrc': item.get('price_rrc', None),
                'quantity': item['quantity'],
                'model': item.get('model', '')
            }
        )

        for param_name, param_value in item.get('parameters', {}).items():
            parameter, _ = Parameter.objects.get_or_create(name=param_name)
            ProductParameter.objects.update_or_create(
                product_info=product_info,
                parameter=parameter,
                defaults={'value': str(param_value)}
            )