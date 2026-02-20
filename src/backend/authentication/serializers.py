from rest_framework import serializers
from .models import User
import re


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя
    """
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'patronymic', 'password', 'password_confirm')

    def validate_email(self, value):
        """Проверка email на уникальность"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_password(self, value):
        """Проверка сложности пароля"""
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен быть не меньше 8 символов")

        # Простая проверка на цифры и буквы
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру")

        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну букву")

        return value

    def validate(self, data):
        """Проверка, что пароли совпадают"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return data

    def create(self, validated_data):
        """Создание пользователя"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)  # bcrypt
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для логина
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя (только чтение)
    """
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'patronymic', 'full_name', 'is_active', 'created_at')
        read_only_fields = ('id', 'email', 'is_active', 'created_at')  # Эти поля нельзя менять через профиль


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления профиля
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'patronymic')