"""
Health models for Scenario 2: Health/Mental-Health Follow-Up.
Tracks patient appointments, follow-ups, and adherence.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import AuditedModel


class Patient(AuditedModel):
    """
    Patient model for health and mental health tracking.
    """
    
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'
    
    patient_id = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique patient identifier'
    )
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    address = models.TextField(blank=True, null=True)
    region = models.CharField(max_length=100)
    
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=20)
    
    registration_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    medical_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['region']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_id})"
    
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


class Appointment(AuditedModel):
    """
    Appointment scheduling and tracking.
    """
    
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        MISSED = 'MISSED', 'Missed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        RESCHEDULED = 'RESCHEDULED', 'Rescheduled'
    
    class AppointmentType(models.TextChoices):
        INITIAL = 'INITIAL', 'Initial Consultation'
        FOLLOW_UP = 'FOLLOW_UP', 'Follow-up'
        EMERGENCY = 'EMERGENCY', 'Emergency'
        ROUTINE = 'ROUTINE', 'Routine Check'
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    
    appointment_type = models.CharField(
        max_length=20,
        choices=AppointmentType.choices
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    
    provider_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    
    reason = models.TextField()
    notes = models.TextField(blank=True, null=True)
    
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'appointments'
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['patient', 'appointment_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.patient} - {self.appointment_date} - {self.status}"


class FollowUpSession(AuditedModel):
    """
    Follow-up session records and outcomes.
    """
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='follow_up_sessions'
    )
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='follow_up_sessions'
    )
    
    session_date = models.DateField()
    session_duration = models.IntegerField(
        help_text='Duration in minutes',
        validators=[MinValueValidator(1)]
    )
    
    provider_name = models.CharField(max_length=200)
    
    symptoms_reported = models.TextField()
    assessment_notes = models.TextField()
    
    mood_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Mood score (1-10)'
    )
    
    anxiety_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Anxiety score (1-10)'
    )
    
    treatment_plan = models.TextField()
    medications_prescribed = models.TextField(blank=True, null=True)
    
    next_appointment_recommended = models.BooleanField(default=True)
    next_appointment_date = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'follow_up_sessions'
        ordering = ['-session_date']
        indexes = [
            models.Index(fields=['patient', 'session_date']),
        ]
    
    def __str__(self):
        return f"{self.patient} - {self.session_date}"


class AdherenceRecord(AuditedModel):
    """
    Track patient adherence to treatment plans and appointments.
    """
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='adherence_records'
    )
    
    assessment_date = models.DateField(auto_now_add=True)
    
    total_appointments = models.IntegerField(default=0)
    attended_appointments = models.IntegerField(default=0)
    missed_appointments = models.IntegerField(default=0)
    
    adherence_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Adherence rate percentage (0-100)'
    )
    
    consecutive_missed = models.IntegerField(
        default=0,
        help_text='Number of consecutive missed appointments'
    )
    
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low Risk'),
            ('MEDIUM', 'Medium Risk'),
            ('HIGH', 'High Risk'),
            ('CRITICAL', 'Critical Risk'),
        ]
    )
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'adherence_records'
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['patient', 'assessment_date']),
            models.Index(fields=['risk_level']),
        ]
    
    def __str__(self):
        return f"{self.patient} - {self.assessment_date} - {self.adherence_rate}%"


class ReferralAction(AuditedModel):
    """
    Referral and reminder actions for missed appointments or low adherence.
    """
    
    class ActionType(models.TextChoices):
        REMINDER = 'REMINDER', 'Reminder Sent'
        REFERRAL = 'REFERRAL', 'Referral Made'
        FOLLOW_UP_CALL = 'FOLLOW_UP_CALL', 'Follow-up Call'
        HOME_VISIT = 'HOME_VISIT', 'Home Visit Scheduled'
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='referral_actions'
    )
    
    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    trigger_reason = models.TextField(
        help_text='Reason for this action (e.g., missed appointment, low adherence)'
    )
    
    action_date = models.DateField()
    completed_date = models.DateField(blank=True, null=True)
    
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_referrals'
    )
    
    outcome = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'referral_actions'
        ordering = ['-action_date']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.patient} - {self.action_type} - {self.status}"
