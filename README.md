# Auth Project
Система аутентификации и авторизации с JWT токенами и ролевым доступом <br>
(проект выполнен на основании ТЗ к Тестовому заданию)

## Статус сборки
![CI/CD Pipeline](https://github.com/DemetriusStorm/auth-project/workflows/CI/CD%20Pipeline/badge.svg)
![Python](https://img.shields.io/badge/python-3.14.0-blue)
![Django](https://img.shields.io/badge/django-6.0.2-green)
![Tests](https://img.shields.io/badge/tests-14%20passed-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-70%25-yellow)

## Содержание

- [Описание проекта](#описание-проекта)
- [Технологии](#технологии)
- [Система разграничения доступа](#система-разграничения-доступа)
- [API endpoints](#api-endpoints)
- [Установка и запуск](#установка-и-запуск)
- [Тестирование](#тестирование)
- [CI/CD](#cicd)

## Описание проекта
Проект реализует собственную систему аутентификации и авторизации без использования встроенных механизмов Django. 

Основные возможности:
- Регистрация, вход, выход
- Управление профилем (обновление, мягкое удаление)
- JWT токены (access 15 мин, refresh 7 дней)
- Ролевая модель (admin, manager, user)
- Система прав доступа к ресурсам
- API для управления правами (только admin)
- Mock объекты для демонстрации

## Технологии
- Python 3.14.0
- Django 6.0.2
- Django REST Framework 3.16.1
- JWT (djangorestframework-simplejwt) 5.5.1
- SQLite (разработка)
- pytest, pytest-cov (тестирование)
- Poetry (управление зависимостями)
- GitHub Actions (CI/CD)


## Система разграничения доступа
### Принцип работы
1. Каждому пользователю назначаются роли (UserRole)
2. Для каждой роли определены правила доступа к ресурсам (AccessRule)
3. При запросе к API проверяется:
   - Аутентификация (JWT токен)
   - Наличие роли с нужными правами
   - Для операций с объектами - проверка владельца

### Правила доступа по умолчанию
#### Роль admin
- Все ресурсы: полный доступ (CRUD) ко всем объектам

#### Роль manager
- products: создание, чтение всех, изменение своих, удаление своих
- orders: создание, чтение всех, изменение своих

#### Роль user
- products: создание, чтение своих, изменение своих, удаление своих
- orders: создание, чтение своих

### Проверка прав в коде
Класс ResourceAccessPermission:
- has_permission - проверка права на действие (create)
- has_object_permission - проверка права на конкретный объект (read, update, delete)
- _is_owner - проверка владельца объекта


## API endpoints
### Аутентификация (authentication)
```
POST /api/auth/register/ # Регистрация
POST /api/auth/login/ # Вход
POST /api/auth/logout/ # Выход
GET /api/auth/profile/ # Получить профиль
PUT /api/auth/profile/ # Обновить профиль
DELETE /api/auth/profile/ # Мягкое удаление аккаунта
POST /api/auth/token/refresh/ # Обновить access token
```

### Управление правами (authorization) - только admin
```
GET /api/authorization/roles/ # Список ролей
POST /api/authorization/roles/ # Создать роль
GET /api/authorization/roles/{id}/ # Получить роль
PUT /api/authorization/roles/{id}/ # Обновить роль
DELETE /api/authorization/roles/{id}/ # Удалить роль

GET /api/authorization/resources/ # Список ресурсов
POST /api/authorization/resources/ # Создать ресурс

GET /api/authorization/access-rules/ # Список правил
POST /api/authorization/access-rules/ # Создать правило
GET /api/authorization/access-rules/check_user_access/ # Проверить доступ

GET /api/authorization/user-roles/ # Список назначений
POST /api/authorization/user-roles/ # Назначить роль
GET /api/authorization/user-roles/user_roles/ # Роли пользователя
```

### Mock объекты (mock_business)
```
GET /api/mock/products/ # Список товаров
POST /api/mock/products/ # Создать товар
GET /api/mock/products/{id}/ # Получить товар
PUT /api/mock/products/{id}/ # Обновить товар
DELETE /api/mock/products/{id}/ # Удалить товар

GET /api/mock/orders/ # Список заказов
POST /api/mock/orders/ # Создать заказ
```

## Установка и запуск
### Предварительные требования

- Python 3.14 или выше
- Poetry (менеджер зависимостей)

### Установка Poetry
```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

## Клонирование и установка
```bash
# Клонировать репозиторий
git clone https://github.com/DemetriusStorm/auth-project.git
cd auth-project
```

```bash
# Установить зависимости
poetry install
```
```bash
# Активировать виртуальное окружение
poetry shell
```
```bash
# Применить миграции
cd src/backend
python manage.py migrate
```
```bash
# Загрузить тестовые данные
python manage.py loaddata authorization/fixtures/initial_data.json
```
```bash
# Создать суперпользователя
python manage.py createsuperuser
# Email: admin@example.com
# Password: Admin123!
```
```bash
# Запустить сервер
python manage.py runserver
```
Сервер будет доступен по адресу http://127.0.0.1:8000

## Назначение ролей
```bash
# Войти в shell Django
python manage.py shell

# Назначить роль admin суперпользователю
from authorization.models import UserRole, Role
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.get(email='admin@example.com')
admin_role = Role.objects.get(name='admin')
UserRole.objects.create(user=admin, role=admin_role, assigned_by=admin)

exit()
```

## Тестирование
### Запуск всех тестов
```bash
# Из папки src/backend
cd src/backend
poetry run pytest ../../tests -v
```
```bash
# Или из корня проекта
cd ../..
poetry run pytest tests/ -v
```
### Запуск с покрытием кода
```bash
poetry run pytest tests/ --cov=authentication --cov=authorization --cov=mock_business --cov-report=html
```
Отчёт появится в папке htmlcov/

### Структура тестов
- tests/unit/test_authentication.py - тесты регистрации, логина, профиля
- tests/unit/test_authorization.py - тесты ролей и прав доступа
- tests/unit/test_mock_business.py - тесты mock объектов и проверки владельца

## CI/CD
### GitHub Actions
При каждом push в ветку main или создании Pull Request автоматически запускается CI пайплайн:
- Установка Python
- Установка зависимостей через Poetry
- Применение миграций
- Загрузка тестовых данных
- Запуск всех тестов
- Сбор отчёта о покрытии кода