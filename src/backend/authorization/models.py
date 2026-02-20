from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class Role(models.Model):
    """
    Роли пользователей в системе
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class BusinessResource(models.Model):
    """
    Бизнес-ресурсы, к которым ограничиваем доступ
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        db_table = 'business_resources'
        verbose_name = 'Бизнес-ресурс'
        verbose_name_plural = 'Бизнес-ресурсы'

    def __str__(self):
        return self.name


class AccessRule(models.Model):
    """
    Правила доступа ролей к ресурсам

    Столбцы с _all означают доступ ко всем объектам этого типа
    Без _all - только к своим (где owner = текущий пользователь)
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='access_rules', verbose_name='Роль')
    resource = models.ForeignKey(BusinessResource, on_delete=models.CASCADE, related_name='access_rules',
                                 verbose_name='Ресурс')

    # CRUD права
    can_create = models.BooleanField(default=False, verbose_name='Может создавать')

    can_read = models.BooleanField(default=False, verbose_name='Может читать свои')
    can_read_all = models.BooleanField(default=False, verbose_name='Может читать все')

    can_update = models.BooleanField(default=False, verbose_name='Может изменять свои')
    can_update_all = models.BooleanField(default=False, verbose_name='Может изменять все')

    can_delete = models.BooleanField(default=False, verbose_name='Может удалять свои')
    can_delete_all = models.BooleanField(default=False, verbose_name='Может удалять все')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        db_table = 'access_rules'
        verbose_name = 'Правило доступа'
        verbose_name_plural = 'Правила доступа'
        unique_together = ('role', 'resource')  # Одно правило на пару роль-ресурс

    def __str__(self):
        return f"{self.role.name} -> {self.resource.name}"


class UserRole(models.Model):
    """
    Назначение ролей пользователям
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles', verbose_name='Пользователь')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles', verbose_name='Роль')
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_roles',
        verbose_name='Кем назначена'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Назначена')

    class Meta:
        db_table = 'user_roles'
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = ('user', 'role')  # Пользователь не может иметь ту же роль дважды

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
