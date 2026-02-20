from .permissions import HasRolePermission
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from .models import Role, BusinessResource, AccessRule, UserRole
from .serializers import (
    RoleSerializer,
    BusinessResourceSerializer,
    AccessRuleSerializer,
    UserRoleSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.
class IsAdminPermission(HasRolePermission):
    """Только для админов"""

    def __init__(self):
        super().__init__(['admin'])


class RoleViewSet(viewsets.ModelViewSet):
    """
    CRUD для ролей (только админ)
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]


class BusinessResourceViewSet(viewsets.ModelViewSet):
    """
    CRUD для бизнес-ресурсов (только админ)
    """
    queryset = BusinessResource.objects.all()
    serializer_class = BusinessResourceSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]


class AccessRuleViewSet(viewsets.ModelViewSet):
    """
    CRUD для правил доступа (только админ)
    """
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]

    @action(detail=False, methods=['get'])
    def check_user_access(self, request):
        """
        Проверка доступа конкретного пользователя к ресурсу
        GET /api/authorization/access-rules/check_user_access/?user_id=1&resource=products&action=read
        """
        user_id = request.query_params.get('user_id')
        resource_name = request.query_params.get('resource')
        action = request.query_params.get('action')

        if not all([user_id, resource_name, action]):
            return Response(
                {'error': 'user_id, resource и action обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, id=user_id)
        resource = get_object_or_404(BusinessResource, name=resource_name)

        # Получаем роли пользователя
        user_roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)

        # Получаем правила для этих ролей
        rules = AccessRule.objects.filter(
            role_id__in=user_roles,
            resource=resource
        )

        # Проверяем права
        has_access = False
        can_access_all = False

        for rule in rules:
            if action == 'create' and rule.can_create:
                has_access = True
            elif action == 'read':
                if rule.can_read_all:
                    has_access = True
                    can_access_all = True
                elif rule.can_read:
                    has_access = True
            elif action == 'update':
                if rule.can_update_all:
                    has_access = True
                    can_access_all = True
                elif rule.can_update:
                    has_access = True
            elif action == 'delete':
                if rule.can_delete_all:
                    has_access = True
                    can_access_all = True
                elif rule.can_delete:
                    has_access = True

        return Response({
            'user_id': user_id,
            'resource': resource_name,
            'action': action,
            'has_access': has_access,
            'can_access_all': can_access_all,
            'roles': list(user_roles)
        })


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    Назначение ролей пользователям (только админ)
    """
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    @action(detail=False, methods=['get'])
    def user_roles(self, request):
        """
        Получить роли конкретного пользователя
        GET /api/authorization/user-roles/user_roles/?user_id=1
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_roles = self.queryset.filter(user_id=user_id)
        serializer = self.get_serializer(user_roles, many=True)
        return Response(serializer.data)
