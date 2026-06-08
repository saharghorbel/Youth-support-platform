"""
Health App Signals
Automatic alerts and actions based on model changes.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Appointment, FollowUpSession, ReferralAction
from core.utils import create_audit_log

User = get_user_model()


@receiver(post_save, sender=Appointment)
def appointment_missed_alert(sender, instance, created, **kwargs):
    """
    Triggered when an Appointment status changes to 'MISSED'.
    Automatically creates a ReferralAction and logs the event.
    """
    # Only trigger if status is MISSED and not a new creation
    if not created and instance.status == 'MISSED':
        # Check if we already created an alert for this appointment
        existing_alert = ReferralAction.objects.filter(
            patient=instance.patient,
            action_type='REMINDER',
            trigger_reason__contains=f"appointment on {instance.appointment_date}"
        ).exists()
        
        if existing_alert:
            # Already created alert, skip
            return
        
        # Find the last assigned supervisor for this patient
        # Try to get from previous referrals
        last_referral = ReferralAction.objects.filter(
            patient=instance.patient,
            assigned_to__isnull=False
        ).order_by('-created_at').first()
        
        if last_referral and last_referral.assigned_to:
            assigned_supervisor = last_referral.assigned_to
        else:
            # Get first available supervisor
            assigned_supervisor = User.objects.filter(
                role=User.Role.SUPERVISOR
            ).first()
        
        # Create automatic referral action
        referral = ReferralAction.objects.create(
            patient=instance.patient,
            action_type='REMINDER',
            status='PENDING',
            trigger_reason=f"Auto-alert: appointment on {instance.appointment_date} was missed",
            action_date=timezone.now().date(),  # Set action_date to today
            assigned_to=assigned_supervisor,
            created_by=instance.created_by if instance.created_by else assigned_supervisor
        )
        
        # Create audit log entry (without request, so no IP/user agent)
        create_audit_log(
            user=instance.created_by if instance.created_by else assigned_supervisor,
            action_type='AUTO_ALERT',
            resource_type='Appointment',
            resource_id=instance.id,
            description=f"Automatic reminder triggered for patient {instance.patient.patient_id} - missed appointment on {instance.appointment_date}",
            result='SUCCESS'
        )


@receiver(post_save, sender=FollowUpSession)
def follow_up_critical_alert(sender, instance, created, **kwargs):
    """
    Triggered when a FollowUpSession is saved.
    If mood_score <= 3 OR anxiety_score >= 8, creates urgent ReferralAction.
    """
    # Check critical mental health indicators
    is_critical = (
        (instance.mood_score is not None and instance.mood_score <= 3) or
        (instance.anxiety_score is not None and instance.anxiety_score >= 8)
    )
    
    if not is_critical:
        return
    
    # Check if we already created an alert for this session
    existing_alert = ReferralAction.objects.filter(
        patient=instance.patient,
        action_type='REFERRAL',
        trigger_reason__contains=f"mood={instance.mood_score}, anxiety={instance.anxiety_score}"
    ).exists()
    
    if existing_alert:
        # Already created alert, skip
        return
    
    # Find the last assigned supervisor for this patient
    last_referral = ReferralAction.objects.filter(
        patient=instance.patient,
        assigned_to__isnull=False
    ).order_by('-created_at').first()
    
    if last_referral and last_referral.assigned_to:
        assigned_supervisor = last_referral.assigned_to
    else:
        # Get first available supervisor
        assigned_supervisor = User.objects.filter(
            role=User.Role.SUPERVISOR
        ).first()
    
    # Create urgent referral action
    referral = ReferralAction.objects.create(
        patient=instance.patient,
        action_type='REFERRAL',
        status='PENDING',
        trigger_reason=f"Critical mental health indicators: mood={instance.mood_score}, anxiety={instance.anxiety_score}",
        action_date=timezone.now().date(),  # Set action_date to today
        assigned_to=assigned_supervisor,
        created_by=instance.created_by if instance.created_by else assigned_supervisor
    )
    
    # Create audit log entry (without request, so no IP/user agent)
    create_audit_log(
        user=instance.created_by if instance.created_by else assigned_supervisor,
        action_type='AUTO_ALERT',
        resource_type='FollowUpSession',
        resource_id=instance.id,
        description=f"Urgent referral triggered for patient {instance.patient.patient_id} - critical indicators: mood={instance.mood_score}, anxiety={instance.anxiety_score}",
        result='SUCCESS'
    )
