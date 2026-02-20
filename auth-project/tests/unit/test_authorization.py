import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from authorization.models import Role, UserRole, AccessRule, BusinessResource
from authorization.permissions import ResourceAccessPermission

User = get_user_model()


@pytest.mark.django_db
class TestAuthorization:
    """Тесты для системы авторизации"""

    @pytest.fixture
    def create_base_data(self):
        """Создаём базовые данные для тестов"""
        # Роли
        admin_role, _ = Role.objects.get_or_create(
            name='admin',
            defaults={'description': 'Admin role'}
        )
        user_role, _ = Role.objects.get_or_create(
            name='user',
            defaults={'description': 'User role'}
        )

        # Ресурсы
        products_resource, _ = BusinessResource.objects.get_or_create(
            name='products',
            defaults={'description': 'Products resource'}
        )

        return {
            'admin_role': admin_role,
            'user_role': user_role,
            'products_resource': products_resource
        }

    @pytest.fixture
    def admin_user(self, create_base_data):
        """Фикстура для создания админа"""
        user = User.objects.create_superuser(
            email='admin@test.ru',
            password='AdminPass123',
            first_name='Admin',
            last_name='Test'
        )
        # Назначаем роль admin
        admin_role = create_base_data['admin_role']
        UserRole.objects.create(
            user=user,
            role=admin_role,
            assigned_by=user
        )
        return user

    @pytest.fixture
    def regular_user(self, create_base_data):
        """Фикстура для обычного пользователя"""
        user = User.objects.create_user(
            email='user@test.ru',
            password='UserPass123',
            first_name='Regular',
            last_name='User'
        )
        # Назначаем роль user
        user_role = create_base_data['user_role']
        UserRole.objects.create(
            user=user,
            role=user_role,
            assigned_by=user
        )
        return user

    def test_admin_can_create_role(self, admin_user):
        """Админ может создавать роли"""
        client = APIClient()
        client.force_authenticate(user=admin_user)

        url = reverse('role-list')
        data = {
            'name': 'testrole',
            'description': 'Test role'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == 201
        assert Role.objects.filter(name='testrole').exists()

    def test_regular_user_cannot_create_role(self, regular_user):
        """Обычный пользователь НЕ может создавать роли"""
        client = APIClient()
        client.force_authenticate(user=regular_user)

        url = reverse('role-list')
        data = {
            'name': 'testrole',
            'description': 'Test role'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == 403

    def test_access_rule_check(self, regular_user, create_base_data):
        """Проверка правил доступа для обычного пользователя"""
        user_role = create_base_data['user_role']
        products_resource = create_base_data['products_resource']

        # Создаём правило доступа
        rule, _ = AccessRule.objects.get_or_create(
            role=user_role,
            resource=products_resource,
            defaults={
                'can_create': True,
                'can_read': True,
                'can_read_all': False,
                'can_update': True,
                'can_update_all': False,
                'can_delete': True,
                'can_delete_all': False
            }
        )

        # Проверяем через API
        client = APIClient()
        client.force_authenticate(user=regular_user)

        # Должен иметь доступ на создание
        perm = ResourceAccessPermission('products', 'create')
        request = type('Request', (), {'user': regular_user})()
        assert perm.has_permission(request, None) == True

        # Не должен иметь доступ на чтение всех
        rules = AccessRule.objects.filter(role=user_role, resource=products_resource)
        assert not any(r.can_read_all for r in rules)