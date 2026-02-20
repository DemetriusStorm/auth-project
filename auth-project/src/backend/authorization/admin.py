from django.contrib import admin
from .models import Role, BusinessResource, AccessRule, UserRole


# Register your models here.
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(BusinessResource)
class BusinessResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    list_display = ('role', 'resource', 'can_create', 'can_read', 'can_read_all',
                    'can_update', 'can_update_all', 'can_delete', 'can_delete_all')
    list_filter = ('role', 'resource')
    search_fields = ('role__name', 'resource__name')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_by', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__email', 'role__name')
