from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


# Register your models here.
class UserAdmin(BaseUserAdmin):
    """
    Настройка отображения модели User в админке
    """
    # Поля, отображаемые в списке пользователей
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')

    # Поля для поиска
    search_fields = ('email', 'first_name', 'last_name')

    # Поля для редактирования
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'patronymic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at', 'deleted_at')}),
    )

    # Поля, доступные только для чтения
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    # Поля при создании нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    # Поле для сортировки по умолчанию
    ordering = ('email',)


# Регистрируем модель в админке
admin.site.register(User, UserAdmin)
