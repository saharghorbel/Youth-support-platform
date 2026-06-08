"""
IMPROVEMENT 6: Synthetic Fixtures Management Command
Load synthetic test data for education and health modules.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import random

from education.models import (
    Student, AttendanceRecord, GradeRecord, BehaviorNote,
    RiskAssessment, InterventionPlan, RiskThreshold
)
from health.models import (
    Patient, Appointment, FollowUpSession, AdherenceRecord, ReferralAction
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Load synthetic fixtures for testing (IMPROVEMENT 6)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=10,
            help='Number of students to create'
        )
        parser.add_argument(
            '--patients',
            type=int,
            default=10,
            help='Number of patients to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading fixtures'
        )

    def handle(self, *args, **options):
        num_students = options['students']
        num_patients = options['patients']
        clear_data = options['clear']

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('IMPROVEMENT 6: Loading Synthetic Fixtures'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Get or create default user
        try:
            default_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            default_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created default admin user'))

        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING('\nClearing existing data...'))
            Student.objects.all().delete()
            Patient.objects.all().delete()
            RiskThreshold.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))

        # Create default risk threshold
        if not RiskThreshold.objects.filter(is_active=True).exists():
            threshold = RiskThreshold.objects.create(
                name='Standard Threshold',
                description='Default threshold for normal operations',
                attendance_threshold=75.0,
                grade_threshold=10.0,
                behavior_threshold=3,
                missed_appointments_threshold=2,
                is_active=True,
                created_by=default_user
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created default risk threshold: {threshold.name}'))

        # Generate students
        self.stdout.write(self.style.SUCCESS(f'\nGenerating {num_students} students...'))
        students = self._generate_students(num_students, default_user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(students)} students'))

        # Generate student data
        self._generate_student_data(students, default_user)

        # Generate patients
        self.stdout.write(self.style.SUCCESS(f'\nGenerating {num_patients} patients...'))
        patients = self._generate_patients(num_patients, default_user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(patients)} patients'))

        # Generate patient data
        self._generate_patient_data(patients, default_user)

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('Fixture loading complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

    def _generate_students(self, count, user):
        """Generate synthetic students."""
        first_names = ['Ahmed', 'Fatima', 'Mohamed', 'Amira', 'Youssef', 'Leila', 'Karim', 'Nour', 'Ali', 'Salma']
        last_names = ['Ben Ali', 'Trabelsi', 'Hamdi', 'Gharbi', 'Mansour', 'Jebali', 'Khelifi', 'Bouazizi']
        schools = ['Lycée Pilote Tunis', 'Lycée Bourguiba', 'Collège Ibn Khaldoun', 'École Primaire Carthage']
        regions = ['Tunis', 'Sfax', 'Sousse', 'Bizerte', 'Gabès']

        students = []
        for i in range(count):
            student = Student.objects.create(
                student_id=f'STU{2026000 + i}',
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                date_of_birth=date.today() - timedelta(days=random.randint(3650, 6570)),  # 10-18 years
                gender=random.choice(['M', 'F']),
                school_name=random.choice(schools),
                grade_level=random.randint(7, 12),
                region=random.choice(regions),
                guardian_name=f'{random.choice(first_names)} {random.choice(last_names)}',
                guardian_phone=f'+216 {random.randint(20, 99)} {random.randint(100, 999)} {random.randint(100, 999)}',
                enrollment_date=date.today() - timedelta(days=random.randint(30, 365)),
                is_active=True,
                created_by=user
            )
            students.append(student)

        return students

    def _generate_student_data(self, students, user):
        """Generate attendance, grades, behavior, and risk assessments for students."""
        self.stdout.write('  Generating attendance records...')
        attendance_count = 0
        for student in students:
            # Generate 30 days of attendance
            for days_ago in range(30):
                attendance_date = date.today() - timedelta(days=days_ago)
                status = random.choices(
                    ['PRESENT', 'ABSENT', 'LATE', 'EXCUSED'],
                    weights=[0.85, 0.05, 0.05, 0.05]
                )[0]
                AttendanceRecord.objects.create(
                    student=student,
                    date=attendance_date,
                    status=status,
                    created_by=user
                )
                attendance_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {attendance_count} attendance records'))

        self.stdout.write('  Generating grade records...')
        grade_count = 0
        subjects = ['Mathematics', 'Physics', 'French', 'Arabic', 'History', 'English']
        for student in students:
            # Generate 5-10 grades
            for _ in range(random.randint(5, 10)):
                GradeRecord.objects.create(
                    student=student,
                    subject=random.choice(subjects),
                    grade=random.uniform(5, 20),
                    exam_date=date.today() - timedelta(days=random.randint(1, 90)),
                    exam_type=random.choice(['QUIZ', 'MIDTERM', 'FINAL', 'PROJECT']),
                    created_by=user
                )
                grade_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {grade_count} grade records'))

        self.stdout.write('  Generating behavior notes...')
        behavior_count = 0
        for student in students:
            # Generate 0-5 behavior notes
            for _ in range(random.randint(0, 5)):
                BehaviorNote.objects.create(
                    student=student,
                    date=date.today() - timedelta(days=random.randint(1, 60)),
                    severity=random.choice(['POSITIVE', 'NEUTRAL', 'MINOR', 'MODERATE', 'SERIOUS']),
                    category=random.choice(['PARTICIPATION', 'CONDUCT', 'SOCIAL', 'MOTIVATION', 'ATTENTION']),
                    description='Synthetic behavior observation for testing purposes.',
                    created_by=user
                )
                behavior_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {behavior_count} behavior notes'))

        self.stdout.write('  Generating risk assessments...')
        assessment_count = 0
        for student in students:
            # Generate 1-3 risk assessments
            for _ in range(random.randint(1, 3)):
                risk_level = random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
                RiskAssessment.objects.create(
                    student=student,
                    attendance_score=random.uniform(50, 100),
                    academic_score=random.uniform(50, 100),
                    behavior_score=random.uniform(50, 100),
                    overall_risk_score=random.uniform(0, 100),
                    risk_level=risk_level,
                    explanation=f'Synthetic risk assessment: {risk_level} risk detected.',
                    recommendations='Monitor closely and provide support as needed.',
                    created_by=user
                )
                assessment_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {assessment_count} risk assessments'))

    def _generate_patients(self, count, user):
        """Generate synthetic patients."""
        first_names = ['Ahmed', 'Fatima', 'Mohamed', 'Amira', 'Youssef', 'Leila', 'Karim', 'Nour', 'Ali', 'Salma']
        last_names = ['Ben Ali', 'Trabelsi', 'Hamdi', 'Gharbi', 'Mansour', 'Jebali', 'Khelifi', 'Bouazizi']
        regions = ['Tunis', 'Sfax', 'Sousse', 'Bizerte', 'Gabès']

        patients = []
        for i in range(count):
            patient = Patient.objects.create(
                patient_id=f'PAT{2026000 + i}',
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                date_of_birth=date.today() - timedelta(days=random.randint(3650, 6570)),  # 10-18 years
                gender=random.choice(['M', 'F']),
                region=random.choice(regions),
                guardian_name=f'{random.choice(first_names)} {random.choice(last_names)}',
                guardian_phone=f'+216 {random.randint(20, 99)} {random.randint(100, 999)} {random.randint(100, 999)}',
                enrollment_date=date.today() - timedelta(days=random.randint(30, 365)),
                is_active=True,
                created_by=user
            )
            patients.append(patient)

        return patients

    def _generate_patient_data(self, patients, user):
        """Generate appointments, follow-ups, and adherence records for patients."""
        self.stdout.write('  Generating appointments...')
        appointment_count = 0
        for patient in patients:
            # Generate 5-10 appointments
            for _ in range(random.randint(5, 10)):
                Appointment.objects.create(
                    patient=patient,
                    appointment_date=date.today() - timedelta(days=random.randint(1, 90)),
                    appointment_type=random.choice(['INITIAL', 'FOLLOW_UP', 'EMERGENCY', 'ROUTINE']),
                    status=random.choices(
                        ['SCHEDULED', 'COMPLETED', 'MISSED', 'CANCELLED'],
                        weights=[0.1, 0.7, 0.1, 0.1]
                    )[0],
                    notes='Synthetic appointment for testing purposes.',
                    created_by=user
                )
                appointment_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {appointment_count} appointments'))

        self.stdout.write('  Generating follow-up sessions...')
        followup_count = 0
        for patient in patients:
            # Generate 2-5 follow-up sessions
            for _ in range(random.randint(2, 5)):
                FollowUpSession.objects.create(
                    patient=patient,
                    session_date=date.today() - timedelta(days=random.randint(1, 60)),
                    session_type=random.choice(['INDIVIDUAL', 'GROUP', 'FAMILY']),
                    mood_score=random.randint(1, 10),
                    anxiety_score=random.randint(1, 10),
                    notes='Synthetic follow-up session for testing purposes.',
                    created_by=user
                )
                followup_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {followup_count} follow-up sessions'))

        self.stdout.write('  Generating adherence records...')
        adherence_count = 0
        for patient in patients:
            # Generate 1-3 adherence records
            for _ in range(random.randint(1, 3)):
                risk_level = random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
                AdherenceRecord.objects.create(
                    patient=patient,
                    adherence_score=random.uniform(50, 100),
                    risk_level=risk_level,
                    explanation=f'Synthetic adherence assessment: {risk_level} risk detected.',
                    recommendations='Continue monitoring and provide support.',
                    created_by=user
                )
                adherence_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {adherence_count} adherence records'))
