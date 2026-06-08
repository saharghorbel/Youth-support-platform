"""
URL configuration for education app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet, AttendanceRecordViewSet, GradeRecordViewSet,
    BehaviorNoteViewSet, RiskAssessmentViewSet, InterventionPlanViewSet
)

app_name = 'education'

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'grades', GradeRecordViewSet, basename='grade')
router.register(r'behavior', BehaviorNoteViewSet, basename='behavior')
router.register(r'risk-assessments', RiskAssessmentViewSet, basename='risk-assessment')
router.register(r'interventions', InterventionPlanViewSet, basename='intervention')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
]
