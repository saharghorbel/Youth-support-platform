"""
Serializers for health app.
"""
from rest_framework import serializers
from .models import (
    Patient, Appointment, FollowUpSession,
    AdherenceRecord, ReferralAction
)


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model."""
    
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'phone_number', 'email',
            'address', 'region', 'emergency_contact_name', 'emergency_contact_phone',
            'registration_date', 'is_active', 'medical_notes',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def validate_patient_id(self, value):
        """Ensure patient_id is unique."""
        if self.instance and self.instance.patient_id == value:
            return value
        if Patient.objects.filter(patient_id=value).exists():
            raise serializers.ValidationError("Patient ID already exists.")
        return value


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'appointment_date', 'appointment_time',
            'appointment_type', 'status', 'provider_name', 'location',
            'reason', 'notes', 'reminder_sent', 'reminder_sent_date',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = [
            'id', 'reminder_sent', 'reminder_sent_date',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]


class FollowUpSessionSerializer(serializers.ModelSerializer):
    """Serializer for FollowUpSession model."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = FollowUpSession
        fields = [
            'id', 'patient', 'patient_name', 'appointment', 'session_date',
            'session_duration', 'provider_name', 'symptoms_reported',
            'assessment_notes', 'mood_score', 'anxiety_score',
            'treatment_plan', 'medications_prescribed',
            'next_appointment_recommended', 'next_appointment_date',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def validate(self, data):
        """Validate mood and anxiety scores."""
        mood_score = data.get('mood_score')
        anxiety_score = data.get('anxiety_score')
        
        if mood_score and (mood_score < 1 or mood_score > 10):
            raise serializers.ValidationError("Mood score must be between 1 and 10.")
        
        if anxiety_score and (anxiety_score < 1 or anxiety_score > 10):
            raise serializers.ValidationError("Anxiety score must be between 1 and 10.")
        
        return data


class AdherenceRecordSerializer(serializers.ModelSerializer):
    """Serializer for AdherenceRecord model."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = AdherenceRecord
        fields = [
            'id', 'patient', 'patient_name', 'assessment_date',
            'total_appointments', 'attended_appointments', 'missed_appointments',
            'adherence_rate', 'consecutive_missed', 'risk_level', 'notes',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'assessment_date', 'created_at', 'updated_at', 'created_by', 'updated_by']


class ReferralActionSerializer(serializers.ModelSerializer):
    """Serializer for ReferralAction model."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = ReferralAction
        fields = [
            'id', 'patient', 'patient_name', 'action_type', 'status',
            'trigger_reason', 'action_date', 'completed_date',
            'assigned_to', 'assigned_to_name', 'outcome',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PatientDetailSerializer(PatientSerializer):
    """Detailed patient serializer with related data."""
    
    upcoming_appointments = AppointmentSerializer(
        source='appointments',
        many=True,
        read_only=True
    )
    recent_sessions = FollowUpSessionSerializer(
        source='follow_up_sessions',
        many=True,
        read_only=True
    )
    latest_adherence = AdherenceRecordSerializer(read_only=True)
    pending_referrals = ReferralActionSerializer(
        many=True,
        read_only=True
    )
    
    class Meta(PatientSerializer.Meta):
        fields = PatientSerializer.Meta.fields + [
            'upcoming_appointments', 'recent_sessions',
            'latest_adherence', 'pending_referrals'
        ]
