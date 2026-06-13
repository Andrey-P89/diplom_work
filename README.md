# Сервис автоматизации закупок (Django REST API)

Дипломный проект профессии «Python-разработчик: расширенный курс».

## Описание

Backend-приложение для заказа товаров в розничной сети. Пользователи (покупатели и поставщики) могут просматривать каталог, формировать корзину, оформлять заказы и получать уведомления по email. Поставщики могут импортировать свои товары из YAML-файлов.

## Технологии

- Python 3.10
- Django 5.2
- Django REST Framework
- SQLite (по умолчанию)
- PyYAML
- Celery
- Redis

## Установка и запуск

1. Клонировать репозиторий:
   ```bash
   git clone <url репозитория>
   cd <папка проекта>
   ```

2. Создать и активировать виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```
3. Установить зависимости:

```bash
pip install -r requirements.txt
```
4. Установить и запустить Redis (брокер сообщений для Celery):

- Linux (Ubuntu):
    ```bash

    sudo apt update
    sudo apt install redis-server
    sudo systemctl start redis
    sudo systemctl enable redis
   ```
- macOS:
    ```bash

    brew install redis
    brew services start redis
    ```

- Windows (WSL или использовать ```memory:// ``` брокер, но рекомендуется Redis через WSL2).
    Проверьте работу: ```redis-cli ping ```→ PONG.
   
5. Запустить Celery worker (в отдельном терминале):
```bash
celery -A main worker --loglevel=info
```

6. Выполнить миграции:

```bash
python manage.py makemigrations users products orders
python manage.py migrate
```
7. Создать суперпользователя (администратора):

```bash
python manage.py createsuperuser
```
8. Загрузить тестовые товары (пример):

```bash
python manage.py import_products 1 data/shop1.yaml
```
9. Запустить сервер:

```bash
python manage.py runserver
```
## API Endpoints (базовые)
POST /api/register/ – регистрация пользователя (email, username, password, password_confirm, type)

POST /api/login/ – получение токена (email, password)

GET /api/products/ – список товаров (фильтрация: ?shop__name=..., поиск: ?search=...)

GET /api/products/<id>/ – детали товара

POST /api/cart/add/ – добавить товар в корзину (product_info_id, quantity)

GET /api/cart/ – просмотр корзины

DELETE /api/cart/remove/<item_id>/ – удалить товар из корзины

POST /api/contacts/ – добавить контакт (адрес доставки: city, street, house, phone и др.)

GET /api/contacts/ – список контактов

DELETE /api/contacts/<id>/ – удалить контакт

POST /api/orders/confirm/ – подтвердить заказ (contact_id)

GET /api/orders/ – список заказов

GET /api/orders/<id>/ – детали заказа

PATCH /api/orders/<id>/status/ – изменить статус заказа (только админ/поставщик)

В файле [`requests.http`](requests.http) приведены готовые примеры всех основных API-вызовов для использования с расширением REST Client в VSCode.  

**Важно:** перед отправкой запросов замените `YOUR_TOKEN_HERE` на реальный токен, полученный при авторизации (`/api/login/`). Первые два запроса (регистрация и логин) не требуют токена.

## Документация API

После запуска сервера интерактивная документация доступна в формате OpenAPI:

- Swagger UI: [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)
- ReDoc: [http://127.0.0.1:8000/api/schema/redoc/](http://127.0.0.1:8000/api/schema/redoc/)
- Схема OpenAPI (JSON): [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

## Email уведомления
При регистрации, оформлении заказа и изменении статуса письма отправляются **асинхронно через Celery**. Для отладки они выводятся в консоль.  
Для отправки реальных писем настройте SMTP в `settings.py`.

## Импорт товаров
Используйте команду 
```bash
python manage.py import_products <user_id> <path_to_yaml>
```

Формат YAML-файла соответствует примеру data/shop1.yaml.