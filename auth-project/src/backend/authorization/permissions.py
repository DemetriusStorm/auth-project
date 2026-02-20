from rest_framework import permissions
from .models import UserRole, AccessRule


class HasRolePermission(permissions.BasePermission):
    """
    Проверка наличия у пользователя определённой роли
    Использование: permission_classes = [HasRolePermission(['admin', 'manager'])]
    """

    def __init__(self, required_roles):
        self.required_roles = required_roles if isinstance(required_roles, list) else [required_roles]

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Получаем все роли пользователя
        user_roles = UserRole.objects.filter(
            user=request.user,
            role__name__in=self.required_roles
        )
        return user_roles.exists()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ResourceAccessPermission(permissions.BasePermission):
    """
    Проверка доступа к конкретному ресурсу
    Использование:
    permission_classes = [ResourceAccessPermission('products', 'read')]
    Где action: 'create', 'read', 'update', 'delete'
    """

    def __init__(self, resource_name, action):
        self.resource_name = resource_name
        self.action = action

    def has_permission(self, request, view):
        """Проверка на уровне всего запроса (для list/create)"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Для действия create проверяем отдельно
        if self.action == 'create':
            return self._check_create_permission(request.user)

        # Для list (read всех) - проверим позже в has_object_permission
        # Но базовое read permission должно быть
        return self._check_read_permission(request.user)

    def has_object_permission(self, request, view, obj):
        """Проверка на уровне конкретного объекта (для retrieve/update/delete)"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Получаем все роли пользователя
        user_roles = UserRole.objects.filter(user=request.user).values_list('role_id', flat=True)

        # Получаем правила доступа для этих ролей и нашего ресурса
        access_rules = AccessRule.objects.filter(
            role_id__in=user_roles,
            resource__name=self.resource_name
        )

        # Проверяем права в зависимости от действия
        if self.action == 'read':
            # Может читать все?
            if any(rule.can_read_all for rule in access_rules):
                return True
            # Может читать свои?
            if any(rule.can_read for rule in access_rules):
                return self._is_owner(request.user, obj)

        elif self.action == 'update':
            if any(rule.can_update_all for rule in access_rules):
                return True
            if any(rule.can_update for rule in access_rules):
                return self._is_owner(request.user, obj)

        elif self.action == 'delete':
            if any(rule.can_delete_all for rule in access_rules):
                return True
            if any(rule.can_delete for rule in access_rules):
                return self._is_owner(request.user, obj)

        return False

    def _check_create_permission(self, user):
        """Проверка права на создание"""
        user_roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
        return AccessRule.objects.filter(
            role_id__in=user_roles,
            resource__name=self.resource_name,
            can_create=True
        ).exists()

    def _check_read_permission(self, user):
        """Базовая проверка права на чтение"""
        user_roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
        return AccessRule.objects.filter(
            role_id__in=user_roles,
            resource__name=self.resource_name,
            can_read__in=[True, False]  # Любое read permission
        ).exists()

    def _is_owner(self, user, obj):
        """Проверка, является ли пользователь владельцем объекта"""
        # Предполагаем, что у объекта есть поле owner или user
        if hasattr(obj, 'owner'):
            return obj.owner == user
        if hasattr(obj, 'user'):
            return obj.user == user
        return False
