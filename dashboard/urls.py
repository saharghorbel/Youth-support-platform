"""
URL configuration for dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('alerts/', views.alerts, name='alerts'),
    path('reports/', views.reports, name='reports'),
    path('api/kpis/', views.kpis_api, name='kpis-api'),
    path('students/', views.students_list, name='students-list'),
    path('students/<int:student_id>/', views.student_detail, name='student-detail'),
    path('patients/', views.patients_list, name='patients-list'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient-detail'),
    path('thresholds/', views.thresholds_list, name='thresholds-list'),
    path('thresholds/<int:threshold_id>/activate/', views.threshold_activate, name='threshold-activate'),
    # IMPROVEMENT 4: Export endpoints
    path('export/students/csv/', views.export_students_csv, name='export-students-csv'),
    path('export/patients/csv/', views.export_patients_csv, name='export-patients-csv'),
    path('export/report/pdf/', views.export_report_pdf, name='export-report-pdf'),
    # IMPROVEMENT 5: Health check endpoint
    path('health/', views.health_check, name='health-check'),
]
