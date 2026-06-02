from django.core.management.base import BaseCommand
from products.import_products import import_products


class Command(BaseCommand):
    help = 'Импорт товаров из YAML файла'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int)
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        import_products(options['user_id'], options['file_path'])
        self.stdout.write(self.style.SUCCESS('Импорт завершён'))