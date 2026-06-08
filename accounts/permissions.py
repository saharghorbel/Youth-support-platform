"""
Custom permissions for role-based access control.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission check for Admin role.
    Only users with ADMIN role can access.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_admin_permission()
        )


class IsSupervisor(permissions.BasePermission):
    """
    Permission check for Supervisor role.
    Users with SUPERVISOR or ADMIN role can access.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_supervisor_permission()
        )


class IsOperator(permissions.BasePermission):
    """
    Permission check for Operator role.
    Users with OPERATOR, SUPERVISOR, or ADMIN role can access.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_operator_permission()
        )


class IsOwnerOrSupervisor(permissions.BasePermission):
    """
    Permission check for object ownership.
    Users can access their own objects, or supervisors can access all.
    """
    
    def has_object_permission(self, request, view, obj):
        # Supervisors and admins can access everything
        if request.user.has_supervisor_permission():
            return True
        
        # Check if object has created_by field
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # Check if object has user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
