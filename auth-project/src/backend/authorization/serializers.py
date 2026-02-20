from rest_framework import serializers
from .models import Role, BusinessResource, AccessRule, UserRole
from django.contrib.auth import get_user_model

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class BusinessResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessResource
        fields = '__all__'


class AccessRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    resource_name = serializers.CharField(source='resource.name', read_only=True)

    class Meta:
        model = AccessRule
        fields = '__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_email = serializers.EmailField(source='assigned_by.email', read_only=True)

    class Meta:
        model = UserRole
        fields = '__all__'
