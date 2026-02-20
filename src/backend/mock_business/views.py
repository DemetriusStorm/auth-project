from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound

from .models import MockProduct, products_db
from authorization.permissions import ResourceAccessPermission


class ProductListView(APIView):
    """
    GET /api/mock/products/ список товаров
    POST /api/mock/products/ создание нового товара
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Проверяем право на чтение товаров
        perm = ResourceAccessPermission('products', 'read')
        if not perm.has_permission(request, self):
            raise PermissionDenied("Нет прав на просмотр товаров")

        # Получаем все товары
        all_products = list(products_db.values())

        # Фильтруем в зависимости от прав
        filtered_products = []
        for product in all_products:
            # Проверяем право на просмотр КОНКРЕТНОГО товара
            if perm.has_object_permission(request, self, product):
                filtered_products.append(product)

        return Response({
            'total': len(filtered_products),
            'products': [p.to_dict() for p in filtered_products]
        })

    def post(self, request):
        # Проверяем право на создание товаров
        perm = ResourceAccessPermission('products', 'create')
        if not perm.has_permission(request, self):
            raise PermissionDenied("Нет прав на создание товаров")

        # Получаем данные из запроса
        name = request.data.get('name')
        price = request.data.get('price')

        if not name or not price:
            return Response(
                {'error': 'Поля name и price обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            price = float(price)
            if price <= 0:
                raise ValueError()
        except ValueError:
            return Response(
                {'error': 'Цена должна быть положительным числом'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаём товар
        product = MockProduct(name, price, request.user)
        products_db[product.id] = product

        return Response(
            product.to_dict(),
            status=status.HTTP_201_CREATED
        )


class ProductDetailView(APIView):
    """
    GET /api/mock/products/{id}/ получить товар
    PUT /api/mock/products/{id}/ обновить товар
    DELETE /api/mock/products/{id}/ удалить товар
    """
    permission_classes = [IsAuthenticated]

    def get_product(self, product_id):
        product = products_db.get(product_id)
        if not product:
            raise NotFound("Товар не найден")
        return product

    def get(self, request, product_id):
        product = self.get_product(product_id)

        # Проверяем право на чтение этого товара
        perm = ResourceAccessPermission('products', 'read')
        if not perm.has_object_permission(request, self, product):
            raise PermissionDenied("Нет прав на просмотр этого товара")

        return Response(product.to_dict())

    def put(self, request, product_id):
        product = self.get_product(product_id)

        # print(f"\n=== PUT Request Debug ===")
        # print(f"Product ID: {product_id}")
        # print(f"Product owner: {product.owner.email}")
        # print(f"Request user: {request.user.email}")
        # print(f"Are they equal? {product.owner == request.user}")

        # Проверяем право на изменение этого товара
        perm = ResourceAccessPermission('products', 'update')
        if not perm.has_object_permission(request, self, product):
            raise PermissionDenied("Нет прав на изменение этого товара")

        # Обновляем поля
        name = request.data.get('name')
        price = request.data.get('price')

        if name:
            product.name = name
        if price:
            try:
                product.price = float(price)
            except ValueError:
                return Response(
                    {'error': 'Цена должна быть числом'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(product.to_dict())

    def delete(self, request, product_id):
        product = self.get_product(product_id)

        # Проверяем право на удаление этого товара
        perm = ResourceAccessPermission('products', 'delete')
        if not perm.has_object_permission(request, self, product):
            raise PermissionDenied("Нет прав на удаление этого товара")

        # Удаляем товар
        del products_db[product_id]

        return Response({'message': 'Товар удалён'}, status=status.HTTP_200_OK)


class OrderListView(APIView):
    """
    GET /api/mock/orders/ список заказов
    POST /api/mock/orders/ создание заказа
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import orders_db
        # from authorization.permissions import ResourceAccessPermission

        # Проверяем право на чтение заказов
        perm = ResourceAccessPermission('orders', 'read')
        if not perm.has_permission(request, self):
            raise PermissionDenied("Нет прав на просмотр заказов")

        all_orders = list(orders_db.values())

        # Фильтруем
        filtered_orders = []
        for order in all_orders:
            if perm.has_object_permission(request, self, order):
                filtered_orders.append(order)

        return Response({
            'total': len(filtered_orders),
            'orders': [o.to_dict() for o in filtered_orders]
        })

    def post(self, request):
        from .models import MockOrder, orders_db, products_db

        # Проверяем право на создание заказов
        perm = ResourceAccessPermission('orders', 'create')
        if not perm.has_permission(request, self):
            raise PermissionDenied("Нет прав на создание заказов")

        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response(
                {'error': 'product_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, что товар существует
        if product_id not in products_db:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            return Response(
                {'error': 'Количество должно быть положительным числом'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаём заказ
        order = MockOrder(product_id, quantity, request.user)
        orders_db[order.id] = order

        return Response(order.to_dict(), status=status.HTTP_201_CREATED)