"""
Views for accounts app.
"""
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from .models import User, AuditLog
from .serializers import (
    UserSerializer, UserCreateSerializer,
    LoginSerializer, AuditLogSerializer
)
from .permissions import IsAdmin
from core.utils import create_audit_log


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management.
    Only admins can create, update, or delete users.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Only admins can modify users."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update current user profile."""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        create_audit_log(
            user=request.user,
            action_type='UPDATE',
            resource_type='User',
            resource_id=str(request.user.id),
            description=f"User {request.user.username} updated their profile",
            result='SUCCESS',
            request=request
        )
        
        return Response(serializer.data)


class LoginView(views.APIView):
    """User login endpoint."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        
        create_audit_log(
            user=user,
            action_type='VIEW',
            resource_type='Auth',
            resource_id=str(user.id),
            description=f"User {user.username} logged in",
            result='SUCCESS',
            request=request
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })


class LogoutView(views.APIView):
    """User logout endpoint."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        create_audit_log(
            user=request.user,
            action_type='VIEW',
            resource_type='Auth',
            resource_id=str(request.user.id),
            description=f"User {request.user.username} logged out",
            result='SUCCESS',
            request=request
        )
        
        logout(request)
        return Response({'message': 'Logout successful'})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs.
    Only admins can view audit logs.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['user', 'action_type', 'resource_type', 'result']
    search_fields = ['description', 'resource_id']
    ordering_fields = ['timestamp']
