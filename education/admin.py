"""
Django admin configuration for education models.
"""
from django.contrib import admin
from .models import (
    Student, AttendanceRecord, GradeRecord, BehaviorNote,
    RiskAssessment, InterventionPlan, RiskThreshold
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model."""
    
    list_display = [
        'student_id', 'full_name', 'school_name', 
        'grade_level', 'region', 'is_active'
    ]
    
    list_filter = [
        'region', 'grade_level', 'gender', 'is_active', 'enrollment_date'
    ]
    
    search_fields = [
        'student_id', 'first_name', 'last_name', 
        'school_name', 'guardian_name'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('School Information', {
            'fields': ('school_name', 'grade_level', 'region', 'enrollment_date', 'is_active')
        }),
        ('Guardian Information', {
            'fields': ('guardian_name', 'guardian_phone', 'guardian_email')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """Admin interface for AttendanceRecord model."""
    
    list_display = ['student', 'date', 'status', 'created_at']
    
    list_filter = ['status', 'date']
    
    search_fields = ['student__first_name', 'student__last_name', 'student__student_id']
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('student', 'date', 'status', 'reason')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GradeRecord)
class GradeRecordAdmin(admin.ModelAdmin):
    """Admin interface for GradeRecord model."""
    
    list_display = ['student', 'subject', 'grade', 'exam_date', 'exam_type']
    
    list_filter = ['exam_type', 'subject', 'exam_date']
    
    search_fields = ['student__first_name', 'student__last_name', 'subject']
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    date_hierarchy = 'exam_date'
    
    fieldsets = (
        ('Grade Information', {
            'fields': ('student', 'subject', 'grade', 'exam_date', 'exam_type')
        }),
        ('Additional Information', {
            'fields': ('comments',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BehaviorNote)
class BehaviorNoteAdmin(admin.ModelAdmin):
    """Admin interface for BehaviorNote model."""
    
    list_display = ['student', 'date', 'severity', 'category', 'created_at']
    
    list_filter = ['severity', 'category', 'date']
    
    search_fields = ['student__first_name', 'student__last_name', 'description']
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Behavior Information', {
            'fields': ('student', 'date', 'severity', 'category')
        }),
        ('Details', {
            'fields': ('description', 'action_taken')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    """Admin interface for RiskAssessment model."""
    
    list_display = [
        'student', 'assessment_date', 'risk_level', 
        'overall_risk_score', 'created_at'
    ]
    
    list_filter = ['risk_level', 'assessment_date']
    
    search_fields = ['student__first_name', 'student__last_name', 'explanation']
    
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'assessment_date']
    
    ordering = ['-assessment_date']
    
    fieldsets = (
        ('Assessment Information', {
            'fields': ('student', 'assessment_date', 'risk_level', 'overall_risk_score')
        }),
        ('Score Breakdown', {
            'fields': ('attendance_score', 'academic_score', 'behavior_score')
        }),
        ('Analysis', {
            'fields': ('explanation', 'recommendations')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InterventionPlan)
class InterventionPlanAdmin(admin.ModelAdmin):
    """Admin interface for InterventionPlan model."""
    
    list_display = [
        'student', 'title', 'status', 
        'start_date', 'assigned_to', 'created_at'
    ]
    
    list_filter = ['status', 'start_date']
    
    search_fields = [
        'student__first_name', 'student__last_name', 
        'title', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Intervention Information', {
            'fields': ('student', 'risk_assessment', 'title', 'description', 'status')
        }),
        ('Timeline', {
            'fields': ('start_date', 'target_end_date', 'actual_end_date')
        }),
        ('Assignment', {
            'fields': ('assigned_to',)
        }),
        ('Plan Details', {
            'fields': ('goals', 'actions')
        }),
        ('Progress', {
            'fields': ('progress_notes', 'outcome')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RiskThreshold)
class RiskThresholdAdmin(admin.ModelAdmin):
    """Admin interface for RiskThreshold model."""
    
    list_display = [
        'name', 'is_active', 'attendance_threshold',
        'grade_threshold', 'behavior_threshold', 
        'missed_appointments_threshold', 'created_at'
    ]
    
    list_filter = ['is_active', 'created_at']
    
    search_fields = ['name', 'description']
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Threshold Configuration', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Threshold Values', {
            'fields': (
                'attendance_threshold', 'grade_threshold',
                'behavior_threshold', 'missed_appointments_threshold'
            )
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by on creation."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
