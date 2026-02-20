import uuid
from datetime import datetime


class MockProduct:
    """
    Мок-модель товара
    """

    def __init__(self, name, price, owner):
        self.id = str(uuid.uuid4())[:8]  # Короткий ID для удобства
        self.name = name
        self.price = float(price)
        self.owner = owner  # Объект User
        self.created_at = datetime.now()

    def to_dict(self):
        """Преобразование в словарь для JSON ответа"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'owner': self.owner.email,
            'created_at': self.created_at.isoformat()
        }

    def __str__(self):
        return f"{self.name} (owner: {self.owner.email})"  # Для отладки


class MockOrder:
    """
    Мок-модель заказа
    """

    def __init__(self, product_id, quantity, owner):
        self.id = str(uuid.uuid4())[:8]
        self.product_id = product_id
        self.quantity = quantity
        self.owner = owner
        self.status = 'pending'  # pending, completed, cancelled
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'status': self.status,
            'owner': self.owner.email,
            'created_at': self.created_at.isoformat()
        }


# Хранилище
products_db = {}  # {product_id: MockProduct}
orders_db = {}  # {order_id: MockOrder}
