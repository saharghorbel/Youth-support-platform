"""
Django admin configuration for health models.
"""
from django.contrib import admin
from .models import (
    Patient, Appointment, FollowUpSession, 
    AdherenceRecord, ReferralAction
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin interface for Patient model."""
    
    list_display = [
        'patient_id', 'full_name', 'region', 
        'registration_date', 'is_active'
    ]
    
    list_filter = ['region', 'gender', 'is_active', 'registration_date']
    
    search_fields = [
        'patient_id', 'first_name', 'last_name', 
        'phone_number', 'emergency_contact_name'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_id', 'first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address', 'region')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Registration', {
            'fields': ('registration_date', 'is_active')
        }),
        ('Medical Information', {
            'fields': ('medical_notes',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin interface for Appointment model."""
    
    list_display = [
        'patient', 'appointment_date', 'appointment_time',
        'appointment_type', 'status', 'provider_name'
    ]
    
    list_filter = ['status', 'appointment_type', 'appointment_date']
    
    search_fields = [
        'patient__first_name', 'patient__last_name', 
        'provider_name', 'location'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Appointment Information', {
            'fields': (
                'patient', 'appointment_date', 'appointment_time',
                'appointment_type', 'status'
            )
        }),
        ('Provider Information', {
            'fields': ('provider_name', 'location')
        }),
        ('Details', {
            'fields': ('reason', 'notes')
        }),
        ('Reminder', {
            'fields': ('reminder_sent', 'reminder_sent_date')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FollowUpSession)
class FollowUpSessionAdmin(admin.ModelAdmin):
    """Admin interface for FollowUpSession model."""
    
    list_display = [
        'patient', 'session_date', 'mood_score', 
        'anxiety_score', 'provider_name'
    ]
    
    list_filter = ['session_date', 'mood_score', 'anxiety_score']
    
    search_fields = [
        'patient__first_name', 'patient__last_name', 
        'provider_name', 'symptoms_reported'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    date_hierarchy = 'session_date'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('patient', 'appointment', 'session_date', 'session_duration', 'provider_name')
        }),
        ('Assessment', {
            'fields': ('symptoms_reported', 'assessment_notes', 'mood_score', 'anxiety_score')
        }),
        ('Treatment', {
            'fields': ('treatment_plan', 'medications_prescribed')
        }),
        ('Follow-up', {
            'fields': ('next_appointment_recommended', 'next_appointment_date')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AdherenceRecord)
class AdherenceRecordAdmin(admin.ModelAdmin):
    """Admin interface for AdherenceRecord model."""
    
    list_display = [
        'patient', 'assessment_date', 'risk_level', 
        'adherence_rate', 'missed_appointments'
    ]
    
    list_filter = ['risk_level', 'assessment_date']
    
    search_fields = ['patient__first_name', 'patient__last_name']
    
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'assessment_date']
    
    ordering = ['-assessment_date']
    
    fieldsets = (
        ('Adherence Information', {
            'fields': (
                'patient', 'assessment_date', 'risk_level', 'adherence_rate'
            )
        }),
        ('Appointment Statistics', {
            'fields': (
                'total_appointments', 'attended_appointments', 
                'missed_appointments', 'consecutive_missed'
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReferralAction)
class ReferralActionAdmin(admin.ModelAdmin):
    """Admin interface for ReferralAction model."""
    
    list_display = [
        'patient', 'action_type', 'status', 
        'action_date', 'assigned_to'
    ]
    
    list_filter = ['action_type', 'status', 'action_date']
    
    search_fields = [
        'patient__first_name', 'patient__last_name', 
        'trigger_reason', 'outcome'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    date_hierarchy = 'action_date'
    
    fieldsets = (
        ('Referral Information', {
            'fields': ('patient', 'action_type', 'status', 'trigger_reason')
        }),
        ('Timeline', {
            'fields': ('action_date', 'completed_date')
        }),
        ('Assignment', {
            'fields': ('assigned_to',)
        }),
        ('Outcome', {
            'fields': ('outcome',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
