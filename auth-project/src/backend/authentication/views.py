from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate

from .models import User
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    LoginSerializer,
    UserUpdateSerializer
)


# Create your views here.
def get_tokens_for_user(user):
    """
    Вспомогательная функция для получения JWT токенов
    """
    refresh = RefreshToken.for_user(user)

    # Можно добавить дополнительные данные в токен
    refresh['email'] = user.email

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@api_view(['POST'])
@permission_classes([AllowAny])  # Разрешаем всем
def register(request):
    """
    Регистрация нового пользователя
    POST /api/auth/register/
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)

        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Вход пользователя
    POST /api/auth/login/
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            # Ищем пользователя по email
            user = User.objects.get(email=email)

            # Проверяем пароль
            if not user.check_password(password):
                return Response(
                    {'error': 'Неверный email или пароль'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Проверяем активен ли пользователь
            if not user.is_active:
                return Response(
                    {'error': 'Аккаунт деактивирован'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Всё ОК - генерируем токены
            tokens = get_tokens_for_user(user)

            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': tokens
            })

        except User.DoesNotExist:
            return Response(
                {'error': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    """
    Выход пользователя
    POST /api/auth/logout/

    TODO: При использовании JWT, клиент просто должен забыть токены.
        Но можно добавить blacklist для refresh токенов (сделать позже)
    """
    # Пытаемся добавить refresh токен в blacklist, если он передан
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Работает если включен blacklist app
    except Exception:
        pass  # Игнорируем ошибки при blacklist'е

    return Response({'message': 'Успешный выход из системы'})


@api_view(['GET', 'PUT', 'DELETE'])
def profile(request):
    """
    Управление профилем пользователя
    GET - получить профиль
    PUT - обновить профиль
    DELETE - мягко удалить аккаунт (деактивировать)
    """
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # "Мягкое" удаление
        request.user.soft_delete()
        return Response(
            {'message': 'Аккаунт успешно деактивирован'},
            status=status.HTTP_200_OK
        )

    return None
