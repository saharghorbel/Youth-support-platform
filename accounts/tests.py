"""
Tests for accounts app with failure injection.
"""
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User, AuditLog


class UserModelTest(TestCase):
    """Test User model and permissions."""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role=User.Role.ADMIN
        )
        self.supervisor = User.objects.create_user(
            username='supervisor',
            password='super123',
            role=User.Role.SUPERVISOR
        )
        self.operator = User.objects.create_user(
            username='operator',
            password='oper123',
            role=User.Role.OPERATOR
        )
    
    def test_user_creation(self):
        """Test user can be created with correct role."""
        self.assertEqual(self.admin.role, User.Role.ADMIN)
        self.assertEqual(self.supervisor.role, User.Role.SUPERVISOR)
        self.assertEqual(self.operator.role, User.Role.OPERATOR)
    
    def test_admin_permissions(self):
        """Test admin has all permissions."""
        self.assertTrue(self.admin.has_admin_permission())
        self.assertTrue(self.admin.has_supervisor_permission())
        self.assertTrue(self.admin.has_operator_permission())
    
    def test_supervisor_permissions(self):
        """Test supervisor has supervisor and operator permissions."""
        self.assertFalse(self.supervisor.has_admin_permission())
        self.assertTrue(self.supervisor.has_supervisor_permission())
        self.assertTrue(self.supervisor.has_operator_permission())
    
    def test_operator_permissions(self):
        """Test operator has only operator permissions."""
        self.assertFalse(self.operator.has_admin_permission())
        self.assertFalse(self.operator.has_supervisor_permission())
        self.assertTrue(self.operator.has_operator_permission())


class AuthenticationAPITest(APITestCase):
    """Test authentication endpoints with failure cases."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            role=User.Role.OPERATOR
        )
        self.login_url = reverse('accounts:api-login')
        self.logout_url = reverse('accounts:api-logout')
    
    def test_login_success(self):
        """Test successful login."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_login_invalid_credentials(self):
        """FAILURE CASE: Test login with invalid credentials."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_missing_username(self):
        """FAILURE CASE: Test login with missing username."""
        data = {
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_missing_password(self):
        """FAILURE CASE: Test login with missing password."""
        data = {
            'username': 'testuser'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_inactive_user(self):
        """FAILURE CASE: Test login with inactive user."""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_success(self):
        """Test successful logout."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout_unauthenticated(self):
        """FAILURE CASE: Test logout without authentication."""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserAPITest(APITestCase):
    """Test User API endpoints with permission checks."""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role=User.Role.ADMIN
        )
        self.operator = User.objects.create_user(
            username='operator',
            password='oper123',
            role=User.Role.OPERATOR
        )
        self.users_url = reverse('accounts:user-list')
    
    def test_list_users_as_admin(self):
        """Test admin can list all users."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_list_users_as_operator(self):
        """FAILURE CASE: Test operator cannot list users (permission denied)."""
        self.client.force_authenticate(user=self.operator)
        response = self.client.get(self.users_url)
        # Operators can view but not create/update/delete
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_user_as_admin(self):
        """Test admin can create users."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': User.Role.OPERATOR
        }
        response = self.client.post(self.users_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_user_as_operator(self):
        """FAILURE CASE: Test operator cannot create users."""
        self.client.force_authenticate(user=self.operator)
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'role': User.Role.OPERATOR
        }
        response = self.client.post(self.users_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_user_password_mismatch(self):
        """FAILURE CASE: Test user creation with mismatched passwords."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'role': User.Role.OPERATOR
        }
        response = self.client.post(self.users_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuditLogTest(TestCase):
    """Test audit logging functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_audit_log_creation(self):
        """Test audit log can be created."""
        log = AuditLog.objects.create(
            user=self.user,
            action_type='CREATE',
            resource_type='Student',
            resource_id='123',
            description='Created student',
            result='SUCCESS'
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action_type, 'CREATE')
        self.assertEqual(log.result, 'SUCCESS')
    
    def test_audit_log_failure(self):
        """Test audit log for failed action."""
        log = AuditLog.objects.create(
            user=self.user,
            action_type='UPDATE',
            resource_type='Student',
            resource_id='123',
            description='Failed to update student',
            result='FAILURE',
            reason='Validation error'
        )
        self.assertEqual(log.result, 'FAILURE')
        self.assertIsNotNone(log.reason)
    
    def test_audit_log_blocked_action(self):
        """Test audit log for blocked action."""
        log = AuditLog.objects.create(
            user=self.user,
            action_type='DELETE',
            resource_type='Student',
            resource_id='123',
            description='Attempted to delete student',
            result='BLOCKED',
            reason='Insufficient permissions'
        )
        self.assertEqual(log.result, 'BLOCKED')
