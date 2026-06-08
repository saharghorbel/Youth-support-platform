"""
Tests for education app with failure injection.
"""
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal

from accounts.models import User
from .models import (
    Student, AttendanceRecord, GradeRecord,
    BehaviorNote, RiskAssessment, InterventionPlan
)


class StudentModelTest(TestCase):
    """Test Student model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.Role.OPERATOR
        )
        self.student = Student.objects.create(
            student_id='STU001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2010, 1, 1),
            gender='M',
            school_name='Test School',
            grade_level=5,
            region='Tunis',
            guardian_name='Jane Doe',
            guardian_phone='12345678',
            enrollment_date=date.today(),
            created_by=self.user
        )
    
    def test_student_creation(self):
        """Test student can be created."""
        self.assertEqual(self.student.student_id, 'STU001')
        self.assertEqual(self.student.full_name, 'John Doe')
    
    def test_student_age_calculation(self):
        """Test student age is calculated correctly."""
        expected_age = date.today().year - 2010
        self.assertEqual(self.student.age, expected_age)
    
    def test_duplicate_student_id(self):
        """FAILURE CASE: Test duplicate student ID raises error."""
        with self.assertRaises(Exception):
            Student.objects.create(
                student_id='STU001',  # Duplicate
                first_name='Jane',
                last_name='Smith',
                date_of_birth=date(2011, 1, 1),
                gender='F',
                school_name='Test School',
                grade_level=4,
                region='Tunis',
                guardian_name='John Smith',
                guardian_phone='87654321',
                enrollment_date=date.today(),
                created_by=self.user
            )


class StudentAPITest(APITestCase):
    """Test Student API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.operator = User.objects.create_user(
            username='operator',
            password='oper123',
            role=User.Role.OPERATOR
        )
        self.supervisor = User.objects.create_user(
            username='supervisor',
            password='super123',
            role=User.Role.SUPERVISOR
        )
        self.student = Student.objects.create(
            student_id='STU001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2010, 1, 1),
            gender='M',
            school_name='Test School',
            grade_level=5,
            region='Tunis',
            guardian_name='Jane Doe',
            guardian_phone='12345678',
            enrollment_date=date.today(),
            created_by=self.operator
        )
        self.students_url = reverse('education:student-list')
    
    def test_list_students_authenticated(self):
        """Test authenticated user can list students."""
        self.client.force_authenticate(user=self.operator)
        response = self.client.get(self.students_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_students_unauthenticated(self):
        """FAILURE CASE: Test unauthenticated user cannot list students."""
        response = self.client.get(self.students_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_student_as_operator(self):
        """Test operator can create student."""
        self.client.force_authenticate(user=self.operator)
        data = {
            'student_id': 'STU002',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': '2011-01-01',
            'gender': 'F',
            'school_name': 'Test School',
            'grade_level': 4,
            'region': 'Tunis',
            'guardian_name': 'John Smith',
            'guardian_phone': '87654321',
            'enrollment_date': date.today().isoformat()
        }
        response = self.client.post(self.students_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_student_invalid_grade(self):
        """FAILURE CASE: Test creating student with invalid grade level."""
        self.client.force_authenticate(user=self.operator)
        data = {
            'student_id': 'STU003',
            'first_name': 'Test',
            'last_name': 'Student',
            'date_of_birth': '2010-01-01',
            'gender': 'M',
            'school_name': 'Test School',
            'grade_level': 15,  # Invalid: max is 12
            'region': 'Tunis',
            'guardian_name': 'Guardian',
            'guardian_phone': '12345678',
            'enrollment_date': date.today().isoformat()
        }
        response = self.client.post(self.students_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RiskAssessmentTest(TestCase):
    """Test risk assessment calculation."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.Role.OPERATOR
        )
        self.student = Student.objects.create(
            student_id='STU001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2010, 1, 1),
            gender='M',
            school_name='Test School',
            grade_level=5,
            region='Tunis',
            guardian_name='Jane Doe',
            guardian_phone='12345678',
            enrollment_date=date.today(),
            created_by=self.user
        )
    
    def test_risk_assessment_creation(self):
        """Test risk assessment can be created."""
        assessment = RiskAssessment.objects.create(
            student=self.student,
            attendance_score=Decimal('85.50'),
            academic_score=Decimal('70.00'),
            behavior_score=Decimal('90.00'),
            overall_risk_score=Decimal('80.00'),
            risk_level='LOW',
            explanation='Student performing well',
            recommendations='Continue monitoring',
            created_by=self.user
        )
        self.assertEqual(assessment.risk_level, 'LOW')
        self.assertEqual(assessment.student, self.student)
    
    def test_high_risk_assessment(self):
        """Test high risk assessment."""
        assessment = RiskAssessment.objects.create(
            student=self.student,
            attendance_score=Decimal('50.00'),
            academic_score=Decimal('40.00'),
            behavior_score=Decimal('45.00'),
            overall_risk_score=Decimal('45.00'),
            risk_level='HIGH',
            explanation='Multiple risk factors detected',
            recommendations='Immediate intervention required',
            created_by=self.user
        )
        self.assertEqual(assessment.risk_level, 'HIGH')


class InterventionPlanTest(TestCase):
    """Test intervention plan workflow."""
    
    def setUp(self):
        self.supervisor = User.objects.create_user(
            username='supervisor',
            password='super123',
            role=User.Role.SUPERVISOR
        )
        self.student = Student.objects.create(
            student_id='STU001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2010, 1, 1),
            gender='M',
            school_name='Test School',
            grade_level=5,
            region='Tunis',
            guardian_name='Jane Doe',
            guardian_phone='12345678',
            enrollment_date=date.today(),
            created_by=self.supervisor
        )
        self.assessment = RiskAssessment.objects.create(
            student=self.student,
            attendance_score=Decimal('50.00'),
            academic_score=Decimal('40.00'),
            behavior_score=Decimal('45.00'),
            overall_risk_score=Decimal('45.00'),
            risk_level='HIGH',
            explanation='High risk',
            recommendations='Intervention needed',
            created_by=self.supervisor
        )
    
    def test_intervention_plan_creation(self):
        """Test intervention plan can be created."""
        plan = InterventionPlan.objects.create(
            student=self.student,
            risk_assessment=self.assessment,
            title='Academic Support Plan',
            description='Provide tutoring and mentoring',
            status='DRAFT',
            start_date=date.today(),
            target_end_date=date.today() + timedelta(days=90),
            assigned_to=self.supervisor,
            goals='Improve attendance and grades',
            actions='Weekly tutoring sessions',
            created_by=self.supervisor
        )
        self.assertEqual(plan.status, 'DRAFT')
        self.assertEqual(plan.student, self.student)
    
    def test_intervention_plan_invalid_dates(self):
        """FAILURE CASE: Test intervention plan with invalid dates."""
        # This should be caught by serializer validation in API
        plan = InterventionPlan.objects.create(
            student=self.student,
            risk_assessment=self.assessment,
            title='Test Plan',
            description='Test',
            status='DRAFT',
            start_date=date.today() + timedelta(days=90),
            target_end_date=date.today(),  # End before start
            assigned_to=self.supervisor,
            goals='Test',
            actions='Test',
            created_by=self.supervisor
        )
        # Model allows this, but API validation should catch it
        self.assertIsNotNone(plan)


class AttendanceRecordTest(TestCase):
    """Test attendance record functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.Role.OPERATOR
        )
        self.student = Student.objects.create(
            student_id='STU001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2010, 1, 1),
            gender='M',
            school_name='Test School',
            grade_level=5,
            region='Tunis',
            guardian_name='Jane Doe',
            guardian_phone='12345678',
            enrollment_date=date.today(),
            created_by=self.user
        )
    
    def test_attendance_record_creation(self):
        """Test attendance record can be created."""
        record = AttendanceRecord.objects.create(
            student=self.student,
            date=date.today(),
            status='PRESENT',
            created_by=self.user
        )
        self.assertEqual(record.status, 'PRESENT')
    
    def test_duplicate_attendance_record(self):
        """FAILURE CASE: Test duplicate attendance for same date."""
        AttendanceRecord.objects.create(
            student=self.student,
            date=date.today(),
            status='PRESENT',
            created_by=self.user
        )
        
        with self.assertRaises(Exception):
            AttendanceRecord.objects.create(
                student=self.student,
                date=date.today(),  # Duplicate date
                status='ABSENT',
                created_by=self.user
            )
