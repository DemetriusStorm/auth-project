import pytest
from authorization.models import Role, BusinessResource


@pytest.fixture
def create_test_roles():
    """Создаём тестовые роли"""
    roles = [
        {'name': 'admin', 'description': 'Admin role'},
        {'name': 'user', 'description': 'User role'},
        {'name': 'manager', 'description': 'Manager role'},
    ]

    created_roles = []
    for role_data in roles:
        role, _ = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={'description': role_data['description']}
        )
        created_roles.append(role)

    return created_roles


@pytest.fixture
def create_test_resources():
    """Создаём тестовые ресурсы"""
    resources = [
        {'name': 'products', 'description': 'Products resource'},
        {'name': 'orders', 'description': 'Orders resource'},
    ]

    created_resources = []
    for res_data in resources:
        resource, _ = BusinessResource.objects.get_or_create(
            name=res_data['name'],
            defaults={'description': res_data['description']}
        )
        created_resources.append(resource)

    return created_resources