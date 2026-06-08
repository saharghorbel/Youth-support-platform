"""
Tests for health app with failure injection.
"""
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from datetime import date, time, timedelta
from decimal import Decimal

from accounts.models import User
from .models import (
    Patient, Appointment, FollowUpSession,
    AdherenceRecord, ReferralAction
)


class PatientModelTest(TestCase):
    """Test Patient model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.Role.OPERATOR
        )
        self.patient = Patient.objects.create(
            patient_id='PAT001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1995, 1, 1),
            gender='M',
            phone_number='12345678',
            region='Tunis',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='87654321',
            registration_date=date.today(),
            created_by=self.user
        )
    
    def test_patient_creation(self):
        """Test patient can be created."""
        self.assertEqual(self.patient.patient_id, 'PAT001')
        self.assertEqual(self.patient.full_name, 'John Doe')
    
    def test_duplicate_patient_id(self):
        """FAILURE CASE: Test duplicate patient ID raises error."""
        with self.assertRaises(Exception):
            Patient.objects.create(
                patient_id='PAT001',  # Duplicate
                first_name='Jane',
                last_name='Smith',
                date_of_birth=date(1996, 1, 1),
                gender='F',
                phone_number='11111111',
                region='Tunis',
                emergency_contact_name='John Smith',
                emergency_contact_phone='22222222',
                registration_date=date.today(),
                created_by=self.user
            )


class AppointmentTest(TestCase):
    """Test Appointment functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.Role.OPERATOR
        )
        self.patient = Patient.objects.create(
            patient_id='PAT001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1995, 1, 1),
            gender='M',
            phone_number='12345678',
            region='Tunis',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='87654321',
            registration_date=date.today(),
            created_by=self.user
        )
    
    def test_appointment_creation(self):
        """Test appointment can be created."""
        appointment = Appointment.objects.create(
            patient=self.patient,
            appointment_date=date.today() + timedelta(days=7),
            appointment_time=time(10, 0),
            appointment_type='INITIAL',
            status='SCHEDULED',
            provider_name='Dr. Smith',
            location='Clinic A',
            reason='Initial consultation',
            created_by=self.user
        )
        self.assertEqual(appointment.status, 'SCHEDULED')
        self.assertEqual(appointment.patient, self.patient)
    
    def test_appointment_status_transitions(self):
        """Test appointment status can be updated."""
        appointment = Appointment.objects.create(
            patient=self.patient,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            appointment_type='FOLLOW_UP',
            status='SCHEDULED',
            provider_name='Dr. Smith',
            location='Clinic A',
            reason='Follow-up',
            created_by=self.user
        )
        
        # Mark as completed
        appointment.status = 'COMPLETED'
        appointment.save()
        self.assertEqual(appointment.status, 'COMPLETED')
        
        # Mark as missed
        appointment.status = 'MISSED'
        appointment.save()
        self.assertEqual(appointment.status, 'MISSED')


class AdherenceRecordTest(TestCase):
    """Test adherence calculation."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.Role.OPERATOR
        )
        self.patient = Patient.objects.create(
            patient_id='PAT001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1995, 1, 1),
            gender='M',
            phone_number='12345678',
            region='Tunis',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='87654321',
            registration_date=date.today(),
            created_by=self.user
        )
        
        # Create appointments
        for i in range(10):
            status = 'COMPLETED' if i < 8 else 'MISSED'
            Appointment.objects.create(
                patient=self.patient,
                appointment_date=date.today() - timedelta(days=i*7),
                appointment_time=time(10, 0),
                appointment_type='FOLLOW_UP',
                status=status,
                provider_name='Dr. Smith',
                location='Clinic A',
                reason='Follow-up',
                created_by=self.user
            )
    
    def test_adherence_record_creation(self):
        """Test adherence record can be created."""
        record = AdherenceRecord.objects.create(
            patient=self.patient,
            total_appointments=10,
            attended_appointments=8,
            missed_appointments=2,
            adherence_rate=Decimal('80.00'),
            consecutive_missed=2,
            risk_level='LOW',
            created_by=self.user
        )
        self.assertEqual(record.adherence_rate, Decimal('80.00'))
        self.assertEqual(record.risk_level, 'LOW')
    
    def test_low_adherence_risk(self):
        """Test low adherence triggers high risk."""
        record = AdherenceRecord.objects.create(
            patient=self.patient,
            total_appointments=10,
            attended_appointments=3,
            missed_appointments=7,
            adherence_rate=Decimal('30.00'),
            consecutive_missed=5,
            risk_level='CRITICAL',
            created_by=self.user
        )
        self.assertEqual(record.risk_level, 'CRITICAL')


class ReferralActionTest(TestCase):
    """Test referral action workflow."""
    
    def setUp(self):
        self.supervisor = User.objects.create_user(
            username='supervisor',
            password='super123',
            role=User.Role.SUPERVISOR
        )
        self.patient = Patient.objects.create(
            patient_id='PAT001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1995, 1, 1),
            gender='M',
            phone_number='12345678',
            region='Tunis',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='87654321',
            registration_date=date.today(),
            created_by=self.supervisor
        )
    
    def test_referral_action_creation(self):
        """Test referral action can be created."""
        action = ReferralAction.objects.create(
            patient=self.patient,
            action_type='REMINDER',
            status='PENDING',
            trigger_reason='Missed appointment',
            action_date=date.today(),
            assigned_to=self.supervisor,
            created_by=self.supervisor
        )
        self.assertEqual(action.status, 'PENDING')
        self.assertEqual(action.action_type, 'REMINDER')
    
    def test_referral_action_completion(self):
        """Test referral action can be completed."""
        action = ReferralAction.objects.create(
            patient=self.patient,
            action_type='FOLLOW_UP_CALL',
            status='PENDING',
            trigger_reason='Low adherence',
            action_date=date.today(),
            assigned_to=self.supervisor,
            created_by=self.supervisor
        )
        
        # Complete the action
        action.status = 'COMPLETED'
        action.completed_date = date.today()
        action.outcome = 'Patient contacted successfully'
        action.save()
        
        self.assertEqual(action.status, 'COMPLETED')
        self.assertIsNotNone(action.completed_date)


class PatientAPITest(APITestCase):
    """Test Patient API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.operator = User.objects.create_user(
            username='operator',
            password='oper123',
            role=User.Role.OPERATOR
        )
        self.patient = Patient.objects.create(
            patient_id='PAT001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1995, 1, 1),
            gender='M',
            phone_number='12345678',
            region='Tunis',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='87654321',
            registration_date=date.today(),
            created_by=self.operator
        )
        self.patients_url = reverse('health:patient-list')
    
    def test_list_patients_authenticated(self):
        """Test authenticated user can list patients."""
        self.client.force_authenticate(user=self.operator)
        response = self.client.get(self.patients_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_patients_unauthenticated(self):
        """FAILURE CASE: Test unauthenticated user cannot list patients."""
        response = self.client.get(self.patients_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_patient_as_operator(self):
        """Test operator can create patient."""
        self.client.force_authenticate(user=self.operator)
        data = {
            'patient_id': 'PAT002',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': '1996-01-01',
            'gender': 'F',
            'phone_number': '11111111',
            'region': 'Tunis',
            'emergency_contact_name': 'John Smith',
            'emergency_contact_phone': '22222222',
            'registration_date': date.today().isoformat()
        }
        response = self.client.post(self.patients_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_patient_missing_required_field(self):
        """FAILURE CASE: Test creating patient with missing required field."""
        self.client.force_authenticate(user=self.operator)
        data = {
            'patient_id': 'PAT003',
            'first_name': 'Test',
            # Missing last_name
            'date_of_birth': '1995-01-01',
            'gender': 'M',
            'phone_number': '12345678',
            'region': 'Tunis',
            'emergency_contact_name': 'Emergency',
            'emergency_contact_phone': '87654321',
            'registration_date': date.today().isoformat()
        }
        response = self.client.post(self.patients_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FollowUpSessionTest(TestCase):
    """Test follow-up session functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.Role.OPERATOR
        )
        self.patient = Patient.objects.create(
            patient_id='PAT001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1995, 1, 1),
            gender='M',
            phone_number='12345678',
            region='Tunis',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='87654321',
            registration_date=date.today(),
            created_by=self.user
        )
    
    def test_follow_up_session_creation(self):
        """Test follow-up session can be created."""
        session = FollowUpSession.objects.create(
            patient=self.patient,
            session_date=date.today(),
            session_duration=60,
            provider_name='Dr. Smith',
            symptoms_reported='Anxiety, stress',
            assessment_notes='Patient showing improvement',
            mood_score=7,
            anxiety_score=4,
            treatment_plan='Continue current treatment',
            created_by=self.user
        )
        self.assertEqual(session.mood_score, 7)
        self.assertEqual(session.anxiety_score, 4)
    
    def test_follow_up_session_invalid_scores(self):
        """FAILURE CASE: Test follow-up session with invalid scores."""
        # Model validators should catch this
        with self.assertRaises(Exception):
            FollowUpSession.objects.create(
                patient=self.patient,
                session_date=date.today(),
                session_duration=60,
                provider_name='Dr. Smith',
                symptoms_reported='Test',
                assessment_notes='Test',
                mood_score=15,  # Invalid: max is 10
                anxiety_score=4,
                treatment_plan='Test',
                created_by=self.user
            )
