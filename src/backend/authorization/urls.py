from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'resources', views.BusinessResourceViewSet)
router.register(r'access-rules', views.AccessRuleViewSet)
router.register(r'user-roles', views.UserRoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
