import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestAuthentication:
    """Тесты для аутентификации"""

    def test_user_registration_success(self):
        """Успешная регистрация нового пользователя"""
        client = APIClient()
        url = reverse('register')
        data = {
            'email': 'newuser@example.ru',
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
            'first_name': 'Тест',
            'last_name': 'Тестов'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == 201
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'newuser@example.ru'
        assert User.objects.count() == 1

    def test_user_registration_password_mismatch(self):
        """Ошибка при несовпадении паролей"""
        client = APIClient()
        url = reverse('register')
        data = {
            'email': 'newuser@example.ru',
            'password': 'TestPass123',
            'password_confirm': 'WrongPass123',
            'first_name': 'Тест',
            'last_name': 'Тестов'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == 400
        assert 'password' in response.data

    def test_user_registration_duplicate_email(self):
        """Ошибка при регистрации с существующим email"""
        # Сначала создаём пользователя
        User.objects.create_user(
            email='existing@example.ru',
            password='TestPass123'
        )

        client = APIClient()
        url = reverse('register')
        data = {
            'email': 'existing@example.ru',
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
            'first_name': 'Тест',
            'last_name': 'Тестов'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == 400
        assert 'email' in response.data

    def test_user_login_success(self):
        """Успешный вход в систему"""
        # Создаём пользователя
        user = User.objects.create_user(
            email='login@example.ru',
            password='TestPass123',
            first_name='Логин',
            last_name='Тест'
        )

        client = APIClient()
        url = reverse('login')
        data = {
            'email': 'login@example.ru',
            'password': 'TestPass123'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == 200
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'login@example.ru'

    def test_user_login_wrong_password(self):
        """Ошибка при неправильном пароле"""
        # Создаём пользователя
        user = User.objects.create_user(
            email='login@example.ru',
            password='TestPass123'
        )

        client = APIClient()
        url = reverse('login')
        data = {
            'email': 'login@example.ru',
            'password': 'WrongPass123'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == 401
        assert 'error' in response.data

    def test_user_login_nonexistent_user(self):
        """Ошибка при входе с несуществующим email"""
        client = APIClient()
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.ru',
            'password': 'TestPass123'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == 401
        assert 'error' in response.data

    def test_profile_get_authenticated(self):
        """Получение профиля авторизованным пользователем"""
        # Создаём пользователя и логинимся
        user = User.objects.create_user(
            email='profile@example.ru',
            password='TestPass123',
            first_name='Профиль',
            last_name='Тест'
        )

        client = APIClient()
        # Принудительно авторизуем
        client.force_authenticate(user=user)

        url = reverse('profile')
        response = client.get(url)

        assert response.status_code == 200
        assert response.data['email'] == 'profile@example.ru'
        assert response.data['first_name'] == 'Профиль'

    def test_profile_get_unauthenticated(self):
        """Ошибка при получении профиля без авторизации"""
        client = APIClient()
        url = reverse('profile')
        response = client.get(url)

        assert response.status_code == 401
