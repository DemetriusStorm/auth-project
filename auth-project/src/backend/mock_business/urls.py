from django.urls import path
from . import views

urlpatterns = [
    # Товары
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<str:product_id>/', views.ProductDetailView.as_view(), name='product-detail'),
    # Заказы
    path('orders/', views.OrderListView.as_view(), name='order-list'),
]