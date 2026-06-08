# State Machine Documentation
## Youth Support Platform - SESAME University

**Document Version:** 1.0  
**Last Updated:** May 29, 2026  
**Owner:** Development Team

---

## Purpose

This document describes the state machines used in the Youth Support Platform to manage workflow states and transitions. This is part of **IMPROVEMENT 8** to demonstrate structured workflow management.

---

## 1. Intervention Plan State Machine

### Overview
The `InterventionPlan` model uses a state machine to track the lifecycle of student interventions from creation to completion.

### States

```
┌─────────┐
│  DRAFT  │ ← Initial state when plan is created
└────┬────┘
     │
     ↓
┌─────────┐
│ PENDING │ ← Awaiting supervisor approval
└────┬────┘
     │
     ↓
┌──────────┐
│ APPROVED │ ← Approved and ready to start
└────┬─────┘
     │
     ↓
┌──────────────┐
│ IN_PROGRESS  │ ← Actively being implemented
└────┬─────────┘
     │
     ├──→ ┌───────────┐
     │    │ COMPLETED │ ← Successfully finished
     │    └───────────┘
     │
     └──→ ┌───────────┐
          │ CANCELLED │ ← Terminated before completion
          └───────────┘
```

### State Definitions

| State | Code | Description | Next States |
|-------|------|-------------|-------------|
| Draft | `DRAFT` | Plan is being created, not yet submitted | PENDING, CANCELLED |
| Pending | `PENDING` | Awaiting supervisor approval | APPROVED, CANCELLED |
| Approved | `APPROVED` | Approved by supervisor, ready to start | IN_PROGRESS, CANCELLED |
| In Progress | `IN_PROGRESS` | Actively being implemented | COMPLETED, CANCELLED |
| Completed | `COMPLETED` | Successfully finished | *(terminal state)* |
| Cancelled | `CANCELLED` | Terminated before completion | *(terminal state)* |

### Transitions

#### 1. DRAFT → PENDING
- **Trigger:** User submits plan for approval
- **Conditions:**
  - All required fields filled
  - Valid start and end dates
  - Assigned to a user
- **Actions:**
  - Set status to PENDING
  - Create audit log entry
  - Notify supervisor

#### 2. PENDING → APPROVED
- **Trigger:** Supervisor approves plan
- **Conditions:**
  - User has supervisor permission
  - Plan meets quality standards
- **Actions:**
  - Set status to APPROVED
  - Create audit log entry
  - Notify assigned user

#### 3. APPROVED → IN_PROGRESS
- **Trigger:** Assigned user starts implementation
- **Conditions:**
  - Current date >= start_date
  - Assigned user confirms start
- **Actions:**
  - Set status to IN_PROGRESS
  - Record actual start date
  - Create audit log entry

#### 4. IN_PROGRESS → COMPLETED
- **Trigger:** Assigned user marks as complete
- **Conditions:**
  - Goals achieved
  - Outcome documented
- **Actions:**
  - Set status to COMPLETED
  - Record actual_end_date
  - Create audit log entry
  - Generate completion report

#### 5. ANY → CANCELLED
- **Trigger:** Supervisor or assigned user cancels
- **Conditions:**
  - Valid reason provided
  - Supervisor approval (if not supervisor)
- **Actions:**
  - Set status to CANCELLED
  - Record cancellation reason
  - Create audit log entry
  - Notify stakeholders

### Business Rules

1. **Only supervisors can approve plans**
   - Enforced by `@user_passes_test(is_supervisor)` decorator
   - Permission check: `user.has_supervisor_permission`

2. **Plans cannot be modified after completion**
   - Terminal states (COMPLETED, CANCELLED) are immutable
   - Historical record preserved

3. **Automatic state transitions**
   - No automatic transitions (all manual)
   - Prevents unintended state changes

4. **Audit trail required**
   - Every state transition logged
   - Includes user, timestamp, reason

### Code Example

```python
from education.models import InterventionPlan

# Create new plan (DRAFT)
plan = InterventionPlan.objects.create(
    student=student,
    title="Academic Support Plan",
    status=InterventionPlan.Status.DRAFT,
    # ... other fields
)

# Submit for approval (DRAFT → PENDING)
plan.status = InterventionPlan.Status.PENDING
plan.save()
create_audit_log(user, 'UPDATE', 'InterventionPlan', plan.id, 
                 'Submitted plan for approval', 'SUCCESS')

# Approve plan (PENDING → APPROVED)
if user.has_supervisor_permission:
    plan.status = InterventionPlan.Status.APPROVED
    plan.save()
    create_audit_log(user, 'UPDATE', 'InterventionPlan', plan.id,
                     'Approved intervention plan', 'SUCCESS')

# Start implementation (APPROVED → IN_PROGRESS)
plan.status = InterventionPlan.Status.IN_PROGRESS
plan.save()

# Complete plan (IN_PROGRESS → COMPLETED)
plan.status = InterventionPlan.Status.COMPLETED
plan.actual_end_date = timezone.now().date()
plan.outcome = "Successfully improved attendance and grades"
plan.save()
```

---

## 2. Appointment State Machine

### Overview
The `Appointment` model tracks the lifecycle of patient appointments.

### States

```
┌───────────┐
│ SCHEDULED │ ← Initial state when appointment is booked
└─────┬─────┘
      │
      ├──→ ┌───────────┐
      │    │ COMPLETED │ ← Patient attended appointment
      │    └───────────┘
      │
      ├──→ ┌────────┐
      │    │ MISSED │ ← Patient did not attend
      │    └────────┘
      │         │
      │         └──→ [SIGNAL: appointment_missed_alert]
      │              Creates ReferralAction automatically
      │
      └──→ ┌───────────┐
           │ CANCELLED │ ← Appointment cancelled
           └───────────┘
```

### State Definitions

| State | Code | Description | Next States |
|-------|------|-------------|-------------|
| Scheduled | `SCHEDULED` | Appointment booked | COMPLETED, MISSED, CANCELLED |
| Completed | `COMPLETED` | Patient attended | *(terminal state)* |
| Missed | `MISSED` | Patient did not attend | *(terminal state)* |
| Cancelled | `CANCELLED` | Appointment cancelled | *(terminal state)* |

### Automatic Actions (Django Signals)

#### Signal: appointment_missed_alert
- **Trigger:** Appointment status changed to MISSED
- **Location:** `health/signals.py`
- **Actions:**
  1. Create `ReferralAction` for follow-up
  2. Create audit log entry
  3. Set referral priority to HIGH

```python
@receiver(post_save, sender=Appointment)
def appointment_missed_alert(sender, instance, created, **kwargs):
    if instance.status == 'MISSED':
        # Create automatic referral action
        ReferralAction.objects.create(
            patient=instance.patient,
            action_type='FOLLOW_UP',
            priority='HIGH',
            description=f'Automatic follow-up for missed appointment on {instance.appointment_date}',
            status='PENDING'
        )
```

---

## 3. Risk Assessment State Machine

### Overview
Risk assessments don't have explicit states but follow a lifecycle pattern.

### Lifecycle

```
┌──────────────┐
│   CREATED    │ ← New assessment generated
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   REVIEWED   │ ← Supervisor reviews assessment
└──────┬───────┘
       │
       ├──→ ┌────────────────┐
       │    │ INTERVENTION   │ ← High/Critical risk → Create intervention
       │    │    CREATED     │
       │    └────────────────┘
       │
       └──→ ┌────────────────┐
            │   MONITORED    │ ← Low/Medium risk → Continue monitoring
            └────────────────┘
```

### Risk Level Thresholds

Risk levels are determined by the active `RiskThreshold`:

```python
# Get active threshold
threshold = RiskThreshold.objects.filter(is_active=True).first()

# Calculate risk based on threshold
if attendance_rate < threshold.attendance_threshold:
    # Flag as risk factor
    risk_factors.append('Low attendance')

if average_grade < threshold.grade_threshold:
    # Flag as risk factor
    risk_factors.append('Low grades')
```

### Configurable Thresholds

Supervisors can create and activate different threshold configurations:

| Threshold Type | Attendance | Grade | Behavior | Missed Appts |
|----------------|------------|-------|----------|--------------|
| Standard | 75% | 10/20 | 3 incidents | 2 |
| Strict | 85% | 12/20 | 2 incidents | 1 |
| Lenient | 65% | 8/20 | 5 incidents | 3 |

**Only one threshold can be active at a time.**

---

## 4. Follow-Up Session State Machine

### Overview
Follow-up sessions trigger automatic alerts based on mood/anxiety scores.

### Alert Triggers

```
┌──────────────────┐
│ Session Created  │
└────────┬─────────┘
         │
         ↓
    ┌────────┐
    │ Scores │
    └────┬───┘
         │
         ├──→ mood_score <= 3 OR anxiety_score >= 8
         │    └──→ [SIGNAL: follow_up_critical_alert]
         │         Creates ReferralAction with URGENT priority
         │
         └──→ Normal scores
              └──→ No automatic action
```

### Signal: follow_up_critical_alert
- **Trigger:** Critical mood/anxiety scores detected
- **Location:** `health/signals.py`
- **Conditions:**
  - `mood_score <= 3` (very low mood)
  - OR `anxiety_score >= 8` (very high anxiety)
- **Actions:**
  1. Create `ReferralAction` with URGENT priority
  2. Create audit log entry
  3. Flag for immediate supervisor review

```python
@receiver(post_save, sender=FollowUpSession)
def follow_up_critical_alert(sender, instance, created, **kwargs):
    if created and (instance.mood_score <= 3 or instance.anxiety_score >= 8):
        ReferralAction.objects.create(
            patient=instance.patient,
            action_type='CRISIS',
            priority='URGENT',
            description=f'Critical scores detected: mood={instance.mood_score}, anxiety={instance.anxiety_score}',
            status='PENDING'
        )
```

---

## State Transition Validation

### Validation Rules

1. **Permission Checks**
   ```python
   if not user.has_supervisor_permission:
       raise PermissionDenied("Only supervisors can approve plans")
   ```

2. **State Sequence Validation**
   ```python
   if current_state == 'COMPLETED':
       raise ValidationError("Cannot modify completed plans")
   ```

3. **Required Fields**
   ```python
   if status == 'COMPLETED' and not outcome:
       raise ValidationError("Outcome required for completion")
   ```

4. **Date Validation**
   ```python
   if start_date > target_end_date:
       raise ValidationError("Start date must be before end date")
   ```

---

## Monitoring State Transitions

### Audit Log Queries

```python
from accounts.models import AuditLog

# Track intervention state changes
intervention_changes = AuditLog.objects.filter(
    resource_type='InterventionPlan',
    action_type='UPDATE'
).order_by('-timestamp')

# Find cancelled interventions
cancelled = AuditLog.objects.filter(
    resource_type='InterventionPlan',
    description__icontains='cancelled'
)

# Monitor missed appointments
missed_appointments = AuditLog.objects.filter(
    resource_type='Appointment',
    description__icontains='missed'
)
```

### Dashboard Metrics

- **Pending Interventions:** Count of plans in PENDING state
- **Active Interventions:** Count of plans in IN_PROGRESS state
- **Completion Rate:** COMPLETED / (COMPLETED + CANCELLED) * 100
- **Missed Appointment Rate:** MISSED / (COMPLETED + MISSED) * 100

---

## Best Practices

### 1. Always Log State Transitions
```python
from core.utils import create_audit_log

plan.status = new_status
plan.save()

create_audit_log(
    user=request.user,
    action_type='UPDATE',
    resource_type='InterventionPlan',
    resource_id=plan.id,
    description=f'Changed status from {old_status} to {new_status}',
    result='SUCCESS',
    request=request
)
```

### 2. Validate Before Transition
```python
def can_transition(plan, new_status, user):
    """Check if state transition is allowed."""
    if plan.status == 'COMPLETED':
        return False, "Cannot modify completed plans"
    
    if new_status == 'APPROVED' and not user.has_supervisor_permission:
        return False, "Only supervisors can approve"
    
    return True, None

# Usage
allowed, error = can_transition(plan, 'APPROVED', request.user)
if not allowed:
    messages.error(request, error)
    return redirect('...')
```

### 3. Use Signals for Automatic Actions
```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=MyModel)
def my_signal_handler(sender, instance, created, **kwargs):
    if created:
        # Perform automatic action
        pass
```

### 4. Document State Transitions
- Add comments explaining why transitions occur
- Include business rules in docstrings
- Update this document when adding new states

---

## Testing State Machines

### Unit Tests

```python
from django.test import TestCase
from education.models import InterventionPlan

class InterventionPlanStateTests(TestCase):
    def test_draft_to_pending_transition(self):
        """Test transition from DRAFT to PENDING."""
        plan = InterventionPlan.objects.create(
            status='DRAFT',
            # ... other fields
        )
        
        plan.status = 'PENDING'
        plan.save()
        
        self.assertEqual(plan.status, 'PENDING')
    
    def test_cannot_modify_completed_plan(self):
        """Test that completed plans cannot be modified."""
        plan = InterventionPlan.objects.create(
            status='COMPLETED',
            # ... other fields
        )
        
        with self.assertRaises(ValidationError):
            plan.title = "New Title"
            plan.save()
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-29 | Development Team | Initial state machine documentation (IMPROVEMENT 8) |

---

## References

- Django Signals: https://docs.djangoproject.com/en/stable/topics/signals/
- State Machine Pattern: https://refactoring.guru/design-patterns/state
- Intervention Plan Model: `education/models.py`
- Health Signals: `health/signals.py`
- Audit Logging: `core/utils.py`
