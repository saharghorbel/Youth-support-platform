"""
Education models for Scenario 1: Education Early Warning System.
Tracks student attendance, grades, behavior, and generates risk alerts.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import AuditedModel


class Student(AuditedModel):
    """
    Student model for tracking educational engagement.
    """
    
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'
    
    student_id = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique student identifier'
    )
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    
    school_name = models.CharField(max_length=200)
    grade_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    
    region = models.CharField(
        max_length=100,
        help_text='Geographic region (e.g., Tunis, Sfax, Sousse)'
    )
    
    guardian_name = models.CharField(max_length=200)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField(blank=True, null=True)
    
    enrollment_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'students'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['school_name', 'grade_level']),
            models.Index(fields=['region']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class AttendanceRecord(AuditedModel):
    """
    Daily attendance tracking for students.
    """
    
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        LATE = 'LATE', 'Late'
        EXCUSED = 'EXCUSED', 'Excused Absence'
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices)
    
    reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for absence or lateness'
    )
    
    class Meta:
        db_table = 'attendance_records'
        ordering = ['-date']
        unique_together = ['student', 'date']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class GradeRecord(AuditedModel):
    """
    Academic performance tracking for students.
    """
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='grade_records'
    )
    
    subject = models.CharField(max_length=100)
    
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text='Grade out of 20'
    )
    
    exam_date = models.DateField()
    exam_type = models.CharField(
        max_length=50,
        choices=[
            ('QUIZ', 'Quiz'),
            ('MIDTERM', 'Midterm'),
            ('FINAL', 'Final'),
            ('PROJECT', 'Project'),
        ]
    )
    
    comments = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'grade_records'
        ordering = ['-exam_date']
        indexes = [
            models.Index(fields=['student', 'exam_date']),
            models.Index(fields=['subject']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.subject} - {self.grade}"


class BehaviorNote(AuditedModel):
    """
    Behavioral observations and incidents.
    """
    
    class Severity(models.TextChoices):
        POSITIVE = 'POSITIVE', 'Positive'
        NEUTRAL = 'NEUTRAL', 'Neutral'
        MINOR = 'MINOR', 'Minor Concern'
        MODERATE = 'MODERATE', 'Moderate Concern'
        SERIOUS = 'SERIOUS', 'Serious Concern'
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='behavior_notes'
    )
    
    date = models.DateField()
    severity = models.CharField(max_length=10, choices=Severity.choices)
    
    category = models.CharField(
        max_length=50,
        choices=[
            ('PARTICIPATION', 'Class Participation'),
            ('CONDUCT', 'Conduct'),
            ('SOCIAL', 'Social Interaction'),
            ('MOTIVATION', 'Motivation'),
            ('ATTENTION', 'Attention/Focus'),
        ]
    )
    
    description = models.TextField()
    action_taken = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'behavior_notes'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['severity']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.severity}"


class RiskAssessment(AuditedModel):
    """
    Automated risk assessment for student disengagement.
    """
    
    class RiskLevel(models.TextChoices):
        LOW = 'LOW', 'Low Risk'
        MEDIUM = 'MEDIUM', 'Medium Risk'
        HIGH = 'HIGH', 'High Risk'
        CRITICAL = 'CRITICAL', 'Critical Risk'
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='risk_assessments'
    )
    
    assessment_date = models.DateField(auto_now_add=True)
    
    attendance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Attendance indicator (0-100)'
    )
    
    academic_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Academic performance indicator (0-100)'
    )
    
    behavior_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Behavior indicator (0-100)'
    )
    
    overall_risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Overall risk score (0-100)'
    )
    
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices)
    
    explanation = models.TextField(
        help_text='Human-readable explanation of risk factors'
    )
    
    recommendations = models.TextField(
        help_text='Recommended interventions'
    )
    
    class Meta:
        db_table = 'risk_assessments'
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['student', 'assessment_date']),
            models.Index(fields=['risk_level']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.assessment_date} - {self.risk_level}"


class InterventionPlan(AuditedModel):
    """
    Intervention plans for at-risk students.
    """
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='intervention_plans'
    )
    
    risk_assessment = models.ForeignKey(
        RiskAssessment,
        on_delete=models.SET_NULL,
        null=True,
        related_name='intervention_plans'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    start_date = models.DateField()
    target_end_date = models.DateField()
    actual_end_date = models.DateField(blank=True, null=True)
    
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_interventions'
    )
    
    goals = models.TextField(help_text='Specific, measurable goals')
    actions = models.TextField(help_text='Concrete actions to be taken')
    
    progress_notes = models.TextField(blank=True, null=True)
    outcome = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'intervention_plans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.title} - {self.status}"


class RiskThreshold(models.Model):
    """
    Configurable risk thresholds for the scoring system.
    Only one threshold can be active at a time.
    """
    name = models.CharField(
        max_length=100,
        help_text='Descriptive name for this threshold configuration'
    )
    description = models.TextField(
        blank=True,
        help_text='Explanation of when to use this threshold'
    )
    
    # Threshold values
    attendance_threshold = models.FloatField(
        default=75.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Minimum acceptable attendance rate (%)'
    )
    grade_threshold = models.FloatField(
        default=10.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(20.0)],
        help_text='Minimum acceptable average grade (0-20 scale)'
    )
    behavior_threshold = models.IntegerField(
        default=3,
        validators=[MinValueValidator(0)],
        help_text='Maximum acceptable number of behavior incidents'
    )
    missed_appointments_threshold = models.IntegerField(
        default=2,
        validators=[MinValueValidator(0)],
        help_text='Maximum acceptable number of missed appointments'
    )
    
    # Status
    is_active = models.BooleanField(
        default=False,
        help_text='Only one threshold can be active at a time'
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_thresholds'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'risk_thresholds'
    
    def __str__(self):
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"{self.name} ({status})"
    
    def save(self, *args, **kwargs):
        """Only one threshold can be active at a time."""
        if self.is_active:
            # Deactivate all other thresholds
            RiskThreshold.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
