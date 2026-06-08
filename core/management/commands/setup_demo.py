"""
Management command to set up demo data for the Youth Support Platform.
Creates users, students, patients, and all related data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, timedelta
import random

from education.models import (
    Student, AttendanceRecord, GradeRecord, BehaviorNote,
    RiskAssessment, InterventionPlan
)
from health.models import (
    Patient, Appointment, FollowUpSession, AdherenceRecord, ReferralAction
)
from accounts.models import AuditLog

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up demo data: users, students, patients, and related records'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('SETTING UP DEMO DATA'))
        self.stdout.write(self.style.SUCCESS('Youth Support Platform - SESAME University'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        # Create users
        self.stdout.write(self.style.WARNING('[1/5] Creating users...'))
        users = self._create_users()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(users)} users'))
        self.stdout.write('')

        # Create students
        self.stdout.write(self.style.WARNING('[2/5] Creating students...'))
        students = self._create_students(users['admin'])
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(students)} students'))
        self.stdout.write('')

        # Create student data
        self.stdout.write(self.style.WARNING('[3/5] Creating student data...'))
        self._create_student_data(students, users['admin'])
        self.stdout.write(self.style.SUCCESS('✓ Created attendance, grades, behavior notes, and risk assessments'))
        self.stdout.write('')

        # Create patients
        self.stdout.write(self.style.WARNING('[4/5] Creating patients...'))
        patients = self._create_patients(users['admin'])
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(patients)} patients'))
        self.stdout.write('')

        # Create patient data
        self.stdout.write(self.style.WARNING('[5/5] Creating patient data...'))
        self._create_patient_data(patients, users['admin'])
        self.stdout.write(self.style.SUCCESS('✓ Created appointments, follow-up sessions, and adherence records'))
        self.stdout.write('')

        # Summary
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('DEMO DATA SETUP COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin:      admin / admin123       (role=ADMIN)')
        self.stdout.write('  Counselor:  counselor / counsel123 (role=SUPERVISOR)')
        self.stdout.write('  Teacher:    teacher / teach123     (role=OPERATOR)')
        self.stdout.write('')
        self.stdout.write('Server URL: http://127.0.0.1:8000/')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))

    def _create_users(self):
        """Create the three demo users."""
        users = {}

        # Admin user
        if User.objects.filter(username='admin').exists():
            users['admin'] = User.objects.get(username='admin')
            self.stdout.write('  - admin (already exists)')
        else:
            users['admin'] = User.objects.create_user(
                username='admin',
                email='admin@sesame.edu.tn',
                password='admin123',
                first_name='Admin',
                last_name='Manager',
                role='ADMIN',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write('  - admin (created)')

        # Counselor user (SUPERVISOR)
        if User.objects.filter(username='counselor').exists():
            users['counselor'] = User.objects.get(username='counselor')
            self.stdout.write('  - counselor (already exists)')
        else:
            users['counselor'] = User.objects.create_user(
                username='counselor',
                email='counselor@sesame.edu.tn',
                password='counsel123',
                first_name='Sarah',
                last_name='Counselor',
                role='SUPERVISOR',
                is_staff=True
            )
            self.stdout.write('  - counselor (created)')

        # Teacher user (OPERATOR)
        if User.objects.filter(username='teacher').exists():
            users['teacher'] = User.objects.get(username='teacher')
            self.stdout.write('  - teacher (already exists)')
        else:
            users['teacher'] = User.objects.create_user(
                username='teacher',
                email='teacher@sesame.edu.tn',
                password='teach123',
                first_name='John',
                last_name='Teacher',
                role='OPERATOR',
                is_staff=False
            )
            self.stdout.write('  - teacher (created)')

        return users

    def _create_students(self, created_by):
        """Create 10 synthetic students."""
        first_names = ['Ahmed', 'Fatima', 'Mohamed', 'Amira', 'Youssef', 'Leila', 'Karim', 'Nour', 'Ali', 'Salma']
        last_names = ['Ben Ali', 'Trabelsi', 'Hamdi', 'Gharbi', 'Mansour', 'Jebali', 'Khelifi', 'Bouazizi', 'Sassi', 'Mejri']
        schools = ['Lycée Pilote Tunis', 'Lycée Bourguiba Sfax', 'Collège Ibn Khaldoun', 'École Primaire Carthage']
        regions = ['Tunis', 'Sfax', 'Sousse', 'Bizerte', 'Gabès']

        students = []
        for i in range(10):
            student = Student.objects.create(
                student_id=f'STU2026{str(i+1).zfill(3)}',
                first_name=first_names[i],
                last_name=last_names[i % len(last_names)],
                date_of_birth=date.today() - timedelta(days=random.randint(3650, 6570)),  # 10-18 years
                gender=random.choice(['M', 'F']),
                school_name=random.choice(schools),
                grade_level=random.randint(7, 12),
                region=random.choice(regions),
                guardian_name=f'{random.choice(first_names)} {random.choice(last_names)}',
                guardian_phone=f'+216 {random.randint(20, 99)} {random.randint(100, 999)} {random.randint(100, 999)}',
                enrollment_date=date.today() - timedelta(days=random.randint(30, 365)),
                is_active=True,
                created_by=created_by
            )
            students.append(student)
            self.stdout.write(f'  - {student.student_id}: {student.first_name} {student.last_name}')

        return students

    def _create_student_data(self, students, created_by):
        """Create attendance, grades, behavior notes, and risk assessments."""
        subjects = ['Mathematics', 'Physics', 'French', 'Arabic', 'History', 'English', 'Biology', 'Chemistry']

        for student in students:
            # Create 30 days of attendance records
            for days_ago in range(30):
                attendance_date = date.today() - timedelta(days=days_ago)
                status = random.choices(
                    ['PRESENT', 'ABSENT', 'LATE', 'EXCUSED'],
                    weights=[0.80, 0.10, 0.05, 0.05]
                )[0]
                AttendanceRecord.objects.create(
                    student=student,
                    date=attendance_date,
                    status=status,
                    reason='Synthetic data for demo' if status != 'PRESENT' else '',
                    created_by=created_by
                )

            # Create 8-12 grade records
            for _ in range(random.randint(8, 12)):
                GradeRecord.objects.create(
                    student=student,
                    subject=random.choice(subjects),
                    grade=random.uniform(5, 20),
                    exam_date=date.today() - timedelta(days=random.randint(1, 90)),
                    exam_type=random.choice(['QUIZ', 'MIDTERM', 'FINAL', 'PROJECT']),
                    comments='Synthetic grade for demo',
                    created_by=created_by
                )

            # Create 0-5 behavior notes
            for _ in range(random.randint(0, 5)):
                BehaviorNote.objects.create(
                    student=student,
                    date=date.today() - timedelta(days=random.randint(1, 60)),
                    severity=random.choice(['POSITIVE', 'NEUTRAL', 'MINOR', 'MODERATE', 'SERIOUS']),
                    category=random.choice(['PARTICIPATION', 'CONDUCT', 'SOCIAL', 'MOTIVATION', 'ATTENTION']),
                    description='Synthetic behavior observation for demo purposes.',
                    action_taken='Discussed with student' if random.random() > 0.5 else '',
                    created_by=created_by
                )

            # Create 1-2 risk assessments
            for _ in range(random.randint(1, 2)):
                attendance_score = random.uniform(50, 100)
                academic_score = random.uniform(50, 100)
                behavior_score = random.uniform(50, 100)
                overall_score = (attendance_score + academic_score + behavior_score) / 3

                if overall_score >= 75:
                    risk_level = 'LOW'
                elif overall_score >= 50:
                    risk_level = 'MEDIUM'
                elif overall_score >= 25:
                    risk_level = 'HIGH'
                else:
                    risk_level = 'CRITICAL'

                risk_factors = []
                if attendance_score < 75:
                    risk_factors.append(f'Low attendance ({attendance_score:.1f}%)')
                if academic_score < 60:
                    risk_factors.append(f'Low academic performance ({academic_score:.1f}%)')
                if behavior_score < 70:
                    risk_factors.append(f'Behavior concerns ({behavior_score:.1f}%)')

                explanation = f'Risk level: {risk_level}. '
                if risk_factors:
                    explanation += 'Factors: ' + ', '.join(risk_factors)
                else:
                    explanation += 'Student is performing well across all indicators.'

                RiskAssessment.objects.create(
                    student=student,
                    attendance_score=attendance_score,
                    academic_score=academic_score,
                    behavior_score=behavior_score,
                    overall_risk_score=overall_score,
                    risk_level=risk_level,
                    explanation=explanation,
                    recommendations='Continue monitoring' if risk_level == 'LOW' else 'Intervention recommended',
                    created_by=created_by
                )

    def _create_patients(self, created_by):
        """Create 5 synthetic patients."""
        first_names = ['Sami', 'Ines', 'Rami', 'Hana', 'Tarek']
        last_names = ['Zaidi', 'Mrad', 'Chatti', 'Ferchichi', 'Oueslati']
        regions = ['Tunis', 'Sfax', 'Sousse', 'Bizerte', 'Gabès']

        patients = []
        for i in range(5):
            patient = Patient.objects.create(
                patient_id=f'PAT2026{str(i+1).zfill(3)}',
                first_name=first_names[i],
                last_name=last_names[i],
                date_of_birth=date.today() - timedelta(days=random.randint(3650, 6570)),  # 10-18 years
                gender=random.choice(['M', 'F']),
                phone_number=f'+216 {random.randint(20, 99)} {random.randint(100, 999)} {random.randint(100, 999)}',
                email=f'{first_names[i].lower()}.{last_names[i].lower()}@email.tn',
                address=f'{random.randint(1, 100)} Rue de la République, {random.choice(regions)}',
                region=random.choice(regions),
                emergency_contact_name=f'{random.choice(["Ahmed", "Fatima", "Mohamed"])} {last_names[i]}',
                emergency_contact_phone=f'+216 {random.randint(20, 99)} {random.randint(100, 999)} {random.randint(100, 999)}',
                registration_date=date.today() - timedelta(days=random.randint(30, 365)),
                is_active=True,
                medical_notes='Synthetic patient for demo purposes',
                created_by=created_by
            )
            patients.append(patient)
            self.stdout.write(f'  - {patient.patient_id}: {patient.first_name} {patient.last_name}')

        return patients

    def _create_patient_data(self, patients, created_by):
        """Create appointments, follow-up sessions, and adherence records."""
        providers = ['Dr. Ben Salem', 'Dr. Karray', 'Dr. Mansour', 'Dr. Trabelsi']
        locations = ['Clinique Centrale Tunis', 'Hôpital Habib Thameur', 'Centre de Santé Sfax']

        for patient in patients:
            # Create 8-12 appointments
            total_appointments = 0
            attended_appointments = 0
            missed_appointments = 0

            for _ in range(random.randint(8, 12)):
                appointment_date = date.today() - timedelta(days=random.randint(1, 90))
                appointment_time = time(hour=random.randint(8, 17), minute=random.choice([0, 15, 30, 45]))
                status = random.choices(
                    ['SCHEDULED', 'COMPLETED', 'MISSED', 'CANCELLED'],
                    weights=[0.10, 0.70, 0.10, 0.10]
                )[0]

                total_appointments += 1
                if status == 'COMPLETED':
                    attended_appointments += 1
                elif status == 'MISSED':
                    missed_appointments += 1

                Appointment.objects.create(
                    patient=patient,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    appointment_type=random.choice(['INITIAL', 'FOLLOW_UP', 'EMERGENCY', 'ROUTINE']),
                    status=status,
                    provider_name=random.choice(providers),
                    location=random.choice(locations),
                    reason='Routine check-up' if status != 'EMERGENCY' else 'Emergency consultation',
                    notes='Synthetic appointment for demo purposes.',
                    created_by=created_by
                )

            # Create 5-8 follow-up sessions
            for _ in range(random.randint(5, 8)):
                session_date = date.today() - timedelta(days=random.randint(1, 60))
                mood_score = random.randint(1, 10)
                anxiety_score = random.randint(1, 10)

                FollowUpSession.objects.create(
                    patient=patient,
                    session_date=session_date,
                    session_duration=random.choice([30, 45, 60]),
                    provider_name=random.choice(providers),
                    symptoms_reported='Patient reports feeling ' + random.choice(['better', 'stable', 'anxious', 'stressed']),
                    assessment_notes='Synthetic follow-up session for demo purposes.',
                    mood_score=mood_score,
                    anxiety_score=anxiety_score,
                    treatment_plan='Continue current treatment plan',
                    medications_prescribed='As prescribed' if random.random() > 0.5 else '',
                    next_appointment_recommended=True,
                    next_appointment_date=date.today() + timedelta(days=random.randint(7, 30)),
                    created_by=created_by
                )

            # Create 1-2 adherence records
            for _ in range(random.randint(1, 2)):
                if total_appointments > 0:
                    adherence_rate = (attended_appointments / total_appointments) * 100
                else:
                    adherence_rate = 100.0

                if adherence_rate >= 80:
                    risk_level = 'LOW'
                elif adherence_rate >= 60:
                    risk_level = 'MEDIUM'
                elif adherence_rate >= 40:
                    risk_level = 'HIGH'
                else:
                    risk_level = 'CRITICAL'

                AdherenceRecord.objects.create(
                    patient=patient,
                    total_appointments=total_appointments,
                    attended_appointments=attended_appointments,
                    missed_appointments=missed_appointments,
                    adherence_rate=adherence_rate,
                    consecutive_missed=random.randint(0, 2),
                    risk_level=risk_level,
                    notes=f'Adherence rate: {adherence_rate:.1f}%. Risk level: {risk_level}.',
                    created_by=created_by
                )
