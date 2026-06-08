"""
URL configuration for accounts app.
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginView, LogoutView, AuditLogViewSet

app_name = 'accounts'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    # Web views
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('profile/', UserViewSet.as_view({'get': 'me'}), name='profile'),
    path('settings/', UserViewSet.as_view({'get': 'me'}), name='settings'),
    path('user-list/', UserViewSet.as_view({'get': 'list'}), name='user-list'),
    path('audit-logs/', AuditLogViewSet.as_view({'get': 'list'}), name='audit-logs'),
    
    # API endpoints
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/logout/', LogoutView.as_view(), name='api-logout'),
    path('api/', include(router.urls)),
]
