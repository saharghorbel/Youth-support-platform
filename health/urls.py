"""
URL configuration for health app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, AppointmentViewSet, FollowUpSessionViewSet,
    AdherenceRecordViewSet, ReferralActionViewSet
)

app_name = 'health'

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'follow-ups', FollowUpSessionViewSet, basename='follow-up')
router.register(r'adherence', AdherenceRecordViewSet, basename='adherence')
router.register(r'referrals', ReferralActionViewSet, basename='referral')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
]
