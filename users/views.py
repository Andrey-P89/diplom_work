from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.conf import settings
from .serializers import RegisterSerializer, LoginSerializer
from main.tasks import send_email_task

class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.

    Ожидает POST-запрос с данными:
    - email (обязательное, уникальное)
    - username (обязательное)
    - password (обязательное, минимум 6 символов)
    - password_confirm (должно совпадать с password)
    - type (необязательное, 'buyer' или 'shop', по умолчанию 'buyer')
    - first_name, last_name, company, position (опционально)

    В случае успеха возвращает JSON с данными пользователя и токеном авторизации.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)

        send_email_task.delay(
            subject='Регистрация на сайте',
            message=f'Спасибо за регистрацию, {user.username}!',
            recipient_list=[user.email]
        )
        
        return Response({
            'user': {
                'email': user.email,
                'username': user.username,
                'type': user.type,
                'avatar_url': user.avatar.url if user.avatar else None,
            },
            'token': token.key
        })


class LoginView(generics.GenericAPIView):
    """
    Авторизация пользователя.

    Принимает POST-запрос с полями:
    - email
    - password

    Возвращает токен авторизации, id пользователя, email и тип (buyer/shop).
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'type': user.type,
            'avatar_url': user.avatar.url if user.avatar else None
        })
