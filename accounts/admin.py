"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with role management."""
    
    list_display = ['username', 'email', 'role', 'organization', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'organization']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Organization', {
            'fields': ('role', 'organization', 'phone_number', 'is_active_operator')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Organization', {
            'fields': ('role', 'organization', 'phone_number')
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit log admin for monitoring system actions."""
    
    list_display = ['user', 'action_type', 'resource_type', 'resource_id', 'result', 'timestamp']
    list_filter = ['action_type', 'result', 'resource_type', 'timestamp']
    search_fields = ['user__username', 'resource_id', 'description']
    readonly_fields = ['user', 'action_type', 'resource_type', 'resource_id', 
                       'description', 'result', 'reason', 'ip_address', 
                       'user_agent', 'timestamp']
    
    def has_add_permission(self, request):
        """Audit logs cannot be manually created."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Audit logs cannot be deleted."""
        return False
