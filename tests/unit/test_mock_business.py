import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from mock_business.models import MockProduct, products_db
from authorization.models import Role, UserRole, AccessRule, BusinessResource

User = get_user_model()


@pytest.mark.django_db
class TestMockBusiness:
    """Интеграционные тесты для mock-объектов"""

    @pytest.fixture
    def create_roles_and_resources(self):
        """Создаём роли и ресурсы для тестов"""
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

        # Правила доступа для user
        AccessRule.objects.get_or_create(
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

        # Правила доступа для admin
        AccessRule.objects.get_or_create(
            role=admin_role,
            resource=products_resource,
            defaults={
                'can_create': True,
                'can_read': True,
                'can_read_all': True,
                'can_update': True,
                'can_update_all': True,
                'can_delete': True,
                'can_delete_all': True
            }
        )

        return {
            'admin_role': admin_role,
            'user_role': user_role,
            'products_resource': products_resource
        }

    @pytest.fixture
    def admin_user(self, create_roles_and_resources):
        """Админ"""
        user = User.objects.create_superuser(
            email='admin@test.ru',
            password='AdminPass123'
        )
        admin_role = create_roles_and_resources['admin_role']
        UserRole.objects.create(user=user, role=admin_role, assigned_by=user)
        return user

    @pytest.fixture
    def regular_user(self, create_roles_and_resources):
        """Обычный пользователь"""
        user = User.objects.create_user(
            email='user@test.ru',
            password='UserPass123'
        )
        user_role = create_roles_and_resources['user_role']
        UserRole.objects.create(user=user, role=user_role, assigned_by=user)
        return user

    @pytest.fixture
    def admin_product(self, admin_user):
        """Товар, созданный админом"""
        # Очищаем базу товаров перед тестом
        products_db.clear()
        product = MockProduct("Admin Product", 1000, admin_user)
        products_db[product.id] = product
        return product

    def test_user_cannot_update_admin_product(self, regular_user, admin_product):
        """Обычный пользователь не может изменить товар админа"""
        client = APIClient()
        client.force_authenticate(user=regular_user)

        url = reverse('product-detail', args=[admin_product.id])
        data = {'name': 'Hacked Name'}

        response = client.put(url, data, format='json')

        assert response.status_code == 403

    def test_user_can_update_own_product(self, regular_user):
        """Пользователь может изменить свой товар"""
        # Очищаем базу товаров
        products_db.clear()

        # Создаём свой товар
        product = MockProduct("My Product", 500, regular_user)
        products_db[product.id] = product

        client = APIClient()
        client.force_authenticate(user=regular_user)

        url = reverse('product-detail', args=[product.id])
        data = {'name': 'Updated Name'}

        response = client.put(url, data, format='json')

        assert response.status_code == 200
        assert response.data['name'] == 'Updated Name'

    def test_user_can_create_product(self, regular_user):
        """Пользователь может создать товар"""
        # Очищаем базу товаров
        products_db.clear()

        client = APIClient()
        client.force_authenticate(user=regular_user)

        url = reverse('product-list')
        data = {
            'name': 'New Product',
            'price': 299.99
        }

        response = client.post(url, data, format='json')

        assert response.status_code == 201
        assert response.data['name'] == 'New Product'
        assert response.data['owner'] == regular_user.email
