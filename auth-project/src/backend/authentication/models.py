from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import bcrypt


# Create your models here.
class UserManager(BaseUserManager):
    """
    Кастомный менеджер для создания пользователей
    Нужен, так как используем email вместо username для логина
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя.
    Наследуемся от AbstractBaseUser чтобы полностью контролировать аутентификацию
    PermissionsMixin добавляет поля для прав доступа Django (is_superuser, groups и т.д.)
    """
    email = models.EmailField(unique=True, db_index=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=150, blank=True, verbose_name='Отчество')

    # Флаги состояния
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')  # Для доступа в админку

    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Удалён')

    # Указываем менеджер
    objects = UserManager()

    # Поле для логина (вместо стандартного username)
    USERNAME_FIELD = 'email'
    # Поля, обязательные при создании суперпользователя (кроме password и USERNAME_FIELD)
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'  # Имя таблицы в БД
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        """
        Переопределяем метод установки пароля
        Используем bcrypt вместо стандартного Django hasher'а
        """
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(
            raw_password.encode('utf-8'),
            salt
        ).decode('utf-8')

    def check_password(self, raw_password):
        """
        Переопределяем метод проверки пароля
        """
        return bcrypt.checkpw(
            raw_password.encode('utf-8'),
            self.password.encode('utf-8')
        )

    def soft_delete(self):
        """
        Мягкое удаление пользователя
        """
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    @property
    def full_name(self):
        """
        Возвращает полное имя пользователя
        """
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(filter(None, parts))
