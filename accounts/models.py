"""
User and Role models for the Youth Support Platform.
Implements role-based access control with three main roles:
- Operator: enters and updates records
- Supervisor/Counselor: validates and plans interventions
- Admin/Manager: configures policies and monitors outcomes
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role-based permissions and audit fields.
    """
    
    class Role(models.TextChoices):
        OPERATOR = 'OPERATOR', _('Operator')
        SUPERVISOR = 'SUPERVISOR', _('Supervisor/Counselor')
        ADMIN = 'ADMIN', _('Admin/Manager')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.OPERATOR,
        help_text=_('User role determines access permissions')
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Contact phone number')
    )
    
    organization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Organization or institution name')
    )
    
    is_active_operator = models.BooleanField(
        default=True,
        help_text=_('Designates whether this user can perform operations')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def has_operator_permission(self):
        """Check if user can create and update records."""
        return self.role in [self.Role.OPERATOR, self.Role.SUPERVISOR, self.Role.ADMIN]
    
    def has_supervisor_permission(self):
        """Check if user can validate and plan interventions."""
        return self.role in [self.Role.SUPERVISOR, self.Role.ADMIN]
    
    def has_admin_permission(self):
        """Check if user can configure policies and monitor outcomes."""
        return self.role == self.Role.ADMIN


class AuditLog(models.Model):
    """
    Audit log for tracking all user actions in the system.
    Required for governance and compliance.
    """
    
    class ActionType(models.TextChoices):
        CREATE = 'CREATE', _('Create')
        UPDATE = 'UPDATE', _('Update')
        DELETE = 'DELETE', _('Delete')
        VIEW = 'VIEW', _('View')
        APPROVE = 'APPROVE', _('Approve')
        REJECT = 'REJECT', _('Reject')
        EXPORT = 'EXPORT', _('Export')
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    
    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices
    )
    
    resource_type = models.CharField(
        max_length=100,
        help_text=_('Type of resource affected (e.g., Case, Student, Appointment)')
    )
    
    resource_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        help_text=_('ID of the affected resource')
    )
    
    description = models.TextField(
        help_text=_('Human-readable description of the action')
    )
    
    result = models.CharField(
        max_length=20,
        choices=[
            ('SUCCESS', 'Success'),
            ('FAILURE', 'Failure'),
            ('BLOCKED', 'Blocked'),
        ],
        default='SUCCESS'
    )
    
    reason = models.TextField(
        blank=True,
        null=True,
        help_text=_('Reason for failure or blocking')
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.resource_type} - {self.timestamp}"
