"""
Views for health app - Scenario 2: Health/Mental-Health Follow-Up.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from .models import (
    Patient, Appointment, FollowUpSession,
    AdherenceRecord, ReferralAction
)
from .serializers import (
    PatientSerializer, PatientDetailSerializer,
    AppointmentSerializer, FollowUpSessionSerializer,
    AdherenceRecordSerializer, ReferralActionSerializer
)
from accounts.permissions import IsOperator, IsSupervisor
from core.utils import create_audit_log


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Patient management.
    Operators can create/update, Supervisors can view all.
    """
    queryset = Patient.objects.all()
    permission_classes = [IsAuthenticated, IsOperator]
    filterset_fields = ['region', 'is_active']
    search_fields = ['first_name', 'last_name', 'patient_id']
    ordering_fields = ['last_name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PatientDetailSerializer
        return PatientSerializer
    
    def perform_create(self, serializer):
        """Set created_by field."""
        patient = serializer.save(created_by=self.request.user)
        
        create_audit_log(
            user=self.request.user,
            action_type='CREATE',
            resource_type='Patient',
            resource_id=str(patient.id),
            description=f"Created patient {patient.full_name}",
            result='SUCCESS',
            request=self.request
        )
    
    def perform_update(self, serializer):
        """Set updated_by field."""
        patient = serializer.save(updated_by=self.request.user)
        
        create_audit_log(
            user=self.request.user,
            action_type='UPDATE',
            resource_type='Patient',
            resource_id=str(patient.id),
            description=f"Updated patient {patient.full_name}",
            result='SUCCESS',
            request=self.request
        )
    
    @action(detail=True, methods=['get'])
    def adherence(self, request, pk=None):
        """Get latest adherence record for patient."""
        patient = self.get_object()
        adherence = patient.adherence_records.order_by('-assessment_date').first()
        
        if not adherence:
            return Response(
                {'detail': 'No adherence record found for this patient.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdherenceRecordSerializer(adherence)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def calculate_adherence(self, request, pk=None):
        """Calculate and create new adherence record for patient."""
        patient = self.get_object()
        
        # Get all appointments
        appointments = patient.appointments.all()
        total_appointments = appointments.count()
        
        if total_appointments == 0:
            return Response(
                {'detail': 'No appointments found for this patient.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Count attended and missed
        attended_appointments = appointments.filter(status='COMPLETED').count()
        missed_appointments = appointments.filter(status='MISSED').count()
        
        # Calculate adherence rate
        adherence_rate = (attended_appointments / total_appointments) * 100
        
        # Calculate consecutive missed
        recent_appointments = appointments.order_by('-appointment_date', '-appointment_time')[:10]
        consecutive_missed = 0
        
        for appt in recent_appointments:
            if appt.status == 'MISSED':
                consecutive_missed += 1
            else:
                break
        
        # Determine risk level
        if adherence_rate >= 80 and consecutive_missed == 0:
            risk_level = 'LOW'
        elif adherence_rate >= 60 and consecutive_missed <= 1:
            risk_level = 'MEDIUM'
        elif adherence_rate >= 40 or consecutive_missed <= 2:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'
        
        # Generate notes
        notes = (
            f"Adherence rate: {adherence_rate:.1f}%. "
            f"Attended {attended_appointments} out of {total_appointments} appointments. "
        )
        
        if consecutive_missed > 0:
            notes += f"Consecutive missed appointments: {consecutive_missed}. "
        
        if risk_level in ['HIGH', 'CRITICAL']:
            notes += "Immediate follow-up recommended."
        
        # Create adherence record
        adherence = AdherenceRecord.objects.create(
            patient=patient,
            total_appointments=total_appointments,
            attended_appointments=attended_appointments,
            missed_appointments=missed_appointments,
            adherence_rate=Decimal(str(round(adherence_rate, 2))),
            consecutive_missed=consecutive_missed,
            risk_level=risk_level,
            notes=notes,
            created_by=request.user
        )
        
        # Auto-create referral action if high risk
        if risk_level in ['HIGH', 'CRITICAL']:
            ReferralAction.objects.create(
                patient=patient,
                action_type='FOLLOW_UP_CALL',
                status='PENDING',
                trigger_reason=f"Low adherence rate ({adherence_rate:.1f}%) detected",
                action_date=date.today(),
                assigned_to=request.user,
                created_by=request.user
            )
        
        create_audit_log(
            user=request.user,
            action_type='CREATE',
            resource_type='AdherenceRecord',
            resource_id=str(adherence.id),
            description=f"Calculated adherence for {patient.full_name}: {risk_level}",
            result='SUCCESS',
            request=request
        )
        
        serializer = AdherenceRecordSerializer(adherence)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Appointment management."""
    
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsOperator]
    filterset_fields = ['patient', 'status', 'appointment_type']
    ordering_fields = ['appointment_date', 'appointment_time']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark appointment as completed."""
        appointment = self.get_object()
        appointment.status = 'COMPLETED'
        appointment.updated_by = request.user
        appointment.save()
        
        create_audit_log(
            user=request.user,
            action_type='UPDATE',
            resource_type='Appointment',
            resource_id=str(appointment.id),
            description=f"Marked appointment as completed for {appointment.patient.full_name}",
            result='SUCCESS',
            request=request
        )
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_missed(self, request, pk=None):
        """Mark appointment as missed and trigger referral."""
        appointment = self.get_object()
        appointment.status = 'MISSED'
        appointment.updated_by = request.user
        appointment.save()
        
        # Create referral action
        ReferralAction.objects.create(
            patient=appointment.patient,
            action_type='REMINDER',
            status='PENDING',
            trigger_reason=f"Missed appointment on {appointment.appointment_date}",
            action_date=date.today(),
            assigned_to=request.user,
            created_by=request.user
        )
        
        create_audit_log(
            user=request.user,
            action_type='UPDATE',
            resource_type='Appointment',
            resource_id=str(appointment.id),
            description=f"Marked appointment as missed for {appointment.patient.full_name}",
            result='SUCCESS',
            request=request
        )
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)


class FollowUpSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for FollowUpSession management."""
    
    queryset = FollowUpSession.objects.all()
    serializer_class = FollowUpSessionSerializer
    permission_classes = [IsAuthenticated, IsOperator]
    filterset_fields = ['patient', 'appointment']
    ordering_fields = ['session_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class AdherenceRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing AdherenceRecord (read-only, created via calculate_adherence)."""
    
    queryset = AdherenceRecord.objects.all()
    serializer_class = AdherenceRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['patient', 'risk_level']
    ordering_fields = ['assessment_date', 'adherence_rate']


class ReferralActionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ReferralAction management.
    Supervisors can create and manage referral actions.
    """
    queryset = ReferralAction.objects.all()
    serializer_class = ReferralActionSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]
    filterset_fields = ['patient', 'action_type', 'status', 'assigned_to']
    ordering_fields = ['action_date']
    
    def perform_create(self, serializer):
        """Set created_by field."""
        action = serializer.save(created_by=self.request.user)
        
        create_audit_log(
            user=self.request.user,
            action_type='CREATE',
            resource_type='ReferralAction',
            resource_id=str(action.id),
            description=f"Created referral action for {action.patient.full_name}",
            result='SUCCESS',
            request=self.request
        )
    
    def perform_update(self, serializer):
        """Set updated_by field."""
        action = serializer.save(updated_by=self.request.user)
        
        create_audit_log(
            user=self.request.user,
            action_type='UPDATE',
            resource_type='ReferralAction',
            resource_id=str(action.id),
            description=f"Updated referral action for {action.patient.full_name}",
            result='SUCCESS',
            request=self.request
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark referral action as completed."""
        action = self.get_object()
        outcome = request.data.get('outcome', '')
        
        if action.status == 'COMPLETED':
            return Response(
                {'detail': 'Action is already completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action.status = 'COMPLETED'
        action.completed_date = date.today()
        action.outcome = outcome
        action.updated_by = request.user
        action.save()
        
        create_audit_log(
            user=request.user,
            action_type='UPDATE',
            resource_type='ReferralAction',
            resource_id=str(action.id),
            description=f"Completed referral action for {action.patient.full_name}",
            result='SUCCESS',
            request=request
        )
        
        serializer = self.get_serializer(action)
        return Response(serializer.data)
