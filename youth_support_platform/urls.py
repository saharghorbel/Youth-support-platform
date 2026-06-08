"""
URL configuration for youth_support_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from graphene_django.views import GraphQLView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Redirect root to login
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    
    path('admin/', admin.site.urls),
    
    # Authentication and Dashboard (Web Interface)
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    
    # API endpoints (REST) - using same app URLs
    path('api/accounts/', include('accounts.urls')),
    path('api/education/', include('education.urls')),
    path('api/health/', include('health.urls')),
    path('api/ai/', include('ai_engine.urls')),  # AI Explainable Scoring Engine
    
    # GraphQL endpoint
    path('graphql/', GraphQLView.as_view(graphiql=True)),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
