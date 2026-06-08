"""
Generate realistic synthetic data for Youth Support Platform.
This script creates sample students, patients, and related records for demonstration.
"""
import os
import django
import random
from datetime import date, timedelta, time
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_support_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from education.models import (
    Student, AttendanceRecord, GradeRecord,
    BehaviorNote, RiskAssessment, InterventionPlan
)
from health.models import (
    Patient, Appointment, FollowUpSession,
    AdherenceRecord, ReferralAction
)

User = get_user_model()

# Sample data
TUNISIAN_FIRST_NAMES_MALE = [
    'Mohamed', 'Ahmed', 'Ali', 'Youssef', 'Mehdi', 'Amine', 'Karim', 'Rami',
    'Sami', 'Tarek', 'Walid', 'Zied', 'Hamza', 'Bilel', 'Fares'
]

TUNISIAN_FIRST_NAMES_FEMALE = [
    'Fatma', 'Amira', 'Salma', 'Nour', 'Ines', 'Mariem', 'Yasmine', 'Leila',
    'Sarra', 'Rim', 'Hiba', 'Dorra', 'Emna', 'Nesrine', 'Rahma'
]

TUNISIAN_LAST_NAMES = [
    'Ben Ali', 'Trabelsi', 'Gharbi', 'Jebali', 'Mansouri', 'Bouazizi',
    'Hamdi', 'Karoui', 'Mejri', 'Sassi', 'Dridi', 'Chouchane', 'Oueslati',
    'Bouzid', 'Khelifi', 'Maaloul', 'Slimani', 'Ayari', 'Belhadj', 'Chaabane'
]

TUNISIAN_SCHOOLS = [
    'École Primaire Carthage', 'École Ibn Khaldoun', 'École El Manar',
    'École Bourguiba', 'École La Marsa', 'École Menzah',
    'Collège Sadiki', 'Lycée Pilote Ariana', 'École Bardo'
]

TUNISIAN_REGIONS = [
    'Tunis', 'Ariana', 'Ben Arous', 'Manouba', 'Sfax', 'Sousse',
    'Nabeul', 'Bizerte', 'Kairouan', 'Gabès'
]

SUBJECTS = [
    'Mathematics', 'Arabic', 'French', 'Science', 'History',
    'Geography', 'English', 'Physics', 'Chemistry', 'Biology'
]

BEHAVIOR_CATEGORIES = [
    'PARTICIPATION', 'CONDUCT', 'SOCIAL', 'MOTIVATION', 'ATTENTION'
]

PROVIDERS = [
    'Dr. Amira Mansouri', 'Dr. Mohamed Gharbi', 'Dr. Salma Jebali',
    'Dr. Ahmed Hamdi', 'Dr. Leila Karoui', 'Dr. Youssef Mejri'
]

CLINICS = [
    'Centre de Santé Tunis', 'Clinique La Marsa', 'Hôpital Charles Nicolle',
    'Centre Médical Ariana', 'Clinique Hannibal', 'Centre de Santé Mentale'
]


def get_random_phone():
    """Generate random Tunisian phone number."""
    return f"{random.choice([20, 21, 22, 23, 24, 25, 26, 27, 28, 29])}{random.randint(100000, 999999)}"


def create_users():
    """Create sample users if they don't exist."""
    print("Creating users...")
    
    users = {
        'admin': User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True
            }
        )[0],
        'supervisor1': User.objects.get_or_create(
            username='supervisor1',
            defaults={
                'email': 'supervisor1@example.com',
                'first_name': 'Amira',
                'last_name': 'Mansouri',
                'role': User.Role.SUPERVISOR,
                'organization': 'Ministry of Education'
            }
        )[0],
        'supervisor2': User.objects.get_or_create(
            username='supervisor2',
            defaults={
                'email': 'supervisor2@example.com',
                'first_name': 'Mohamed',
                'last_name': 'Gharbi',
                'role': User.Role.SUPERVISOR,
                'organization': 'Ministry of Health'
            }
        )[0],
        'operator1': User.objects.get_or_create(
            username='operator1',
            defaults={
                'email': 'operator1@example.com',
                'first_name': 'Salma',
                'last_name': 'Jebali',
                'role': User.Role.OPERATOR,
                'organization': 'School Administration'
            }
        )[0],
        'operator2': User.objects.get_or_create(
            username='operator2',
            defaults={
                'email': 'operator2@example.com',
                'first_name': 'Ahmed',
                'last_name': 'Hamdi',
                'role': User.Role.OPERATOR,
                'organization': 'Health Center'
            }
        )[0]
    }
    
    # Set passwords
    for username, user in users.items():
        if username == 'admin':
            user.set_password('admin123')
        elif 'supervisor' in username:
            user.set_password('super123')
        else:
            user.set_password('oper123')
        user.save()
    
    print(f"✓ Created {len(users)} users")
    return users


def create_students(users, count=30):
    """Create sample students."""
    print(f"\nCreating {count} students...")
    
    students = []
    operator = users['operator1']
    
    for i in range(count):
        gender = random.choice(['M', 'F'])
        first_name = random.choice(
            TUNISIAN_FIRST_NAMES_MALE if gender == 'M' else TUNISIAN_FIRST_NAMES_FEMALE
        )
        last_name = random.choice(TUNISIAN_LAST_NAMES)
        
        # Age between 6 and 18
        age = random.randint(6, 18)
        birth_year = date.today().year - age
        date_of_birth = date(birth_year, random.randint(1, 12), random.randint(1, 28))
        
        student = Student.objects.create(
            student_id=f'STU{str(i+1).zfill(4)}',
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            school_name=random.choice(TUNISIAN_SCHOOLS),
            grade_level=min(12, max(1, age - 5)),
            region=random.choice(TUNISIAN_REGIONS),
            guardian_name=f"{random.choice(TUNISIAN_FIRST_NAMES_MALE)} {last_name}",
            guardian_phone=get_random_phone(),
            guardian_email=f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@email.com",
            enrollment_date=date.today() - timedelta(days=random.randint(30, 365)),
            is_active=True,
            created_by=operator
        )
        students.append(student)
    
    print(f"✓ Created {len(students)} students")
    return students


def create_attendance_records(students, users):
    """Create attendance records for students."""
    print("\nCreating attendance records...")
    
    operator = users['operator1']
    records_count = 0
    
    for student in students:
        # Create attendance for last 60 days
        for days_ago in range(60):
            record_date = date.today() - timedelta(days=days_ago)
            
            # Skip weekends
            if record_date.weekday() >= 5:
                continue
            
            # 85% present, 10% absent, 5% late
            status_choice = random.random()
            if status_choice < 0.85:
                status = 'PRESENT'
            elif status_choice < 0.95:
                status = 'ABSENT'
            else:
                status = 'LATE'
            
            AttendanceRecord.objects.create(
                student=student,
                date=record_date,
                status=status,
                reason='Sick' if status == 'ABSENT' and random.random() < 0.5 else '',
                created_by=operator
            )
            records_count += 1
    
    print(f"✓ Created {records_count} attendance records")


def create_grade_records(students, users):
    """Create grade records for students."""
    print("\nCreating grade records...")
    
    operator = users['operator1']
    records_count = 0
    
    for student in students:
        # Create grades for 5 subjects
        for subject in random.sample(SUBJECTS, 5):
            # 2-3 grades per subject
            for _ in range(random.randint(2, 3)):
                # Grade distribution: mostly 10-16, some high, some low
                grade_choice = random.random()
                if grade_choice < 0.7:
                    grade = random.uniform(10, 16)
                elif grade_choice < 0.85:
                    grade = random.uniform(16, 20)
                else:
                    grade = random.uniform(5, 10)
                
                GradeRecord.objects.create(
                    student=student,
                    subject=subject,
                    grade=Decimal(str(round(grade, 2))),
                    exam_date=date.today() - timedelta(days=random.randint(1, 90)),
                    exam_type=random.choice(['QUIZ', 'MIDTERM', 'FINAL', 'PROJECT']),
                    created_by=operator
                )
                records_count += 1
    
    print(f"✓ Created {records_count} grade records")


def create_behavior_notes(students, users):
    """Create behavior notes for some students."""
    print("\nCreating behavior notes...")
    
    operator = users['operator1']
    records_count = 0
    
    # 40% of students have behavior notes
    for student in random.sample(students, int(len(students) * 0.4)):
        # 1-3 notes per student
        for _ in range(random.randint(1, 3)):
            severity = random.choices(
                ['POSITIVE', 'NEUTRAL', 'MINOR', 'MODERATE', 'SERIOUS'],
                weights=[20, 30, 30, 15, 5]
            )[0]
            
            descriptions = {
                'POSITIVE': 'Excellent participation in class',
                'NEUTRAL': 'Normal behavior observed',
                'MINOR': 'Occasional distraction in class',
                'MODERATE': 'Disruptive behavior, needs attention',
                'SERIOUS': 'Serious behavioral issues, immediate intervention needed'
            }
            
            BehaviorNote.objects.create(
                student=student,
                date=date.today() - timedelta(days=random.randint(1, 60)),
                severity=severity,
                category=random.choice(BEHAVIOR_CATEGORIES),
                description=descriptions[severity],
                action_taken='Discussed with student' if severity != 'POSITIVE' else '',
                created_by=operator
            )
            records_count += 1
    
    print(f"✓ Created {records_count} behavior notes")


def create_risk_assessments(students, users):
    """Create risk assessments for students."""
    print("\nCreating risk assessments...")
    
    operator = users['operator1']
    assessments = []
    
    for student in students:
        # Calculate realistic scores
        attendance_score = Decimal(str(random.uniform(60, 100)))
        academic_score = Decimal(str(random.uniform(50, 100)))
        behavior_score = Decimal(str(random.uniform(60, 100)))
        
        overall_score = (attendance_score * Decimal('0.4') + 
                        academic_score * Decimal('0.4') + 
                        behavior_score * Decimal('0.2'))
        
        if overall_score >= 80:
            risk_level = 'LOW'
        elif overall_score >= 60:
            risk_level = 'MEDIUM'
        elif overall_score >= 40:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'
        
        explanations = {
            'LOW': f'Student performing well. Attendance: {attendance_score:.1f}%, Academic: {academic_score:.1f}%',
            'MEDIUM': f'Some concerns detected. Attendance: {attendance_score:.1f}%, Academic: {academic_score:.1f}%',
            'HIGH': f'Multiple risk factors. Low attendance ({attendance_score:.1f}%) and academic performance ({academic_score:.1f}%)',
            'CRITICAL': f'Critical risk level. Immediate intervention required. Attendance: {attendance_score:.1f}%, Academic: {academic_score:.1f}%'
        }
        
        recommendations = {
            'LOW': '- Continue monitoring\n- Maintain current support',
            'MEDIUM': '- Increase monitoring\n- Consider tutoring support',
            'HIGH': '- Immediate tutoring required\n- Contact guardian\n- Weekly progress reviews',
            'CRITICAL': '- Urgent intervention needed\n- Family meeting required\n- Daily monitoring\n- Psychological support'
        }
        
        assessment = RiskAssessment.objects.create(
            student=student,
            attendance_score=attendance_score,
            academic_score=academic_score,
            behavior_score=behavior_score,
            overall_risk_score=overall_score,
            risk_level=risk_level,
            explanation=explanations[risk_level],
            recommendations=recommendations[risk_level],
            created_by=operator
        )
        assessments.append(assessment)
    
    print(f"✓ Created {len(assessments)} risk assessments")
    return assessments


def create_intervention_plans(assessments, users):
    """Create intervention plans for high-risk students."""
    print("\nCreating intervention plans...")
    
    supervisor = users['supervisor1']
    plans = []
    
    # Create plans for HIGH and CRITICAL risk students
    high_risk_assessments = [a for a in assessments if a.risk_level in ['HIGH', 'CRITICAL']]
    
    for assessment in high_risk_assessments:
        status = random.choice(['PENDING', 'APPROVED', 'IN_PROGRESS', 'COMPLETED'])
        
        plan = InterventionPlan.objects.create(
            student=assessment.student,
            risk_assessment=assessment,
            title=f'Support Plan for {assessment.student.full_name}',
            description=f'Comprehensive intervention plan to address {assessment.risk_level.lower()} risk factors',
            status=status,
            start_date=date.today() + timedelta(days=random.randint(1, 7)),
            target_end_date=date.today() + timedelta(days=random.randint(60, 120)),
            actual_end_date=date.today() if status == 'COMPLETED' else None,
            assigned_to=supervisor,
            goals='Improve attendance to 90%\nIncrease academic performance\nAddress behavioral concerns',
            actions='Weekly tutoring sessions\nBi-weekly family meetings\nDaily attendance monitoring',
            progress_notes='Plan initiated' if status != 'DRAFT' else '',
            outcome='Significant improvement observed' if status == 'COMPLETED' else '',
            created_by=supervisor
        )
        plans.append(plan)
    
    print(f"✓ Created {len(plans)} intervention plans")


def create_patients(users, count=20):
    """Create sample patients."""
    print(f"\nCreating {count} patients...")
    
    patients = []
    operator = users['operator2']
    
    for i in range(count):
        gender = random.choice(['M', 'F'])
        first_name = random.choice(
            TUNISIAN_FIRST_NAMES_MALE if gender == 'M' else TUNISIAN_FIRST_NAMES_FEMALE
        )
        last_name = random.choice(TUNISIAN_LAST_NAMES)
        
        # Age between 15 and 25
        age = random.randint(15, 25)
        birth_year = date.today().year - age
        date_of_birth = date(birth_year, random.randint(1, 12), random.randint(1, 28))
        
        patient = Patient.objects.create(
            patient_id=f'PAT{str(i+1).zfill(4)}',
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            phone_number=get_random_phone(),
            email=f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@email.com",
            region=random.choice(TUNISIAN_REGIONS),
            emergency_contact_name=f"{random.choice(TUNISIAN_FIRST_NAMES_MALE)} {last_name}",
            emergency_contact_phone=get_random_phone(),
            registration_date=date.today() - timedelta(days=random.randint(30, 365)),
            is_active=True,
            medical_notes='Initial consultation completed',
            created_by=operator
        )
        patients.append(patient)
    
    print(f"✓ Created {len(patients)} patients")
    return patients


def create_appointments(patients, users):
    """Create appointments for patients."""
    print("\nCreating appointments...")
    
    operator = users['operator2']
    appointments = []
    
    for patient in patients:
        # 3-8 appointments per patient
        num_appointments = random.randint(3, 8)
        
        for i in range(num_appointments):
            days_ago = random.randint(1, 180)
            appt_date = date.today() - timedelta(days=days_ago)
            
            # 70% completed, 20% missed, 10% scheduled
            status_choice = random.random()
            if days_ago > 7:
                if status_choice < 0.7:
                    status = 'COMPLETED'
                elif status_choice < 0.9:
                    status = 'MISSED'
                else:
                    status = 'CANCELLED'
            else:
                status = 'SCHEDULED'
            
            appointment = Appointment.objects.create(
                patient=patient,
                appointment_date=appt_date,
                appointment_time=time(random.randint(8, 17), random.choice([0, 30])),
                appointment_type='INITIAL' if i == 0 else random.choice(['FOLLOW_UP', 'ROUTINE']),
                status=status,
                provider_name=random.choice(PROVIDERS),
                location=random.choice(CLINICS),
                reason='Mental health consultation' if i == 0 else 'Follow-up session',
                created_by=operator
            )
            appointments.append(appointment)
    
    print(f"✓ Created {len(appointments)} appointments")
    return appointments


def create_follow_up_sessions(appointments, users):
    """Create follow-up sessions for completed appointments."""
    print("\nCreating follow-up sessions...")
    
    operator = users['operator2']
    sessions = []
    
    completed_appointments = [a for a in appointments if a.status == 'COMPLETED']
    
    # 60% of completed appointments have follow-up sessions
    for appointment in random.sample(completed_appointments, int(len(completed_appointments) * 0.6)):
        session = FollowUpSession.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            session_date=appointment.appointment_date,
            session_duration=random.choice([30, 45, 60]),
            provider_name=appointment.provider_name,
            symptoms_reported=random.choice([
                'Anxiety, stress',
                'Depression symptoms',
                'Sleep difficulties',
                'Mood swings',
                'General well-being check'
            ]),
            assessment_notes='Patient showing progress' if random.random() < 0.7 else 'Needs continued support',
            mood_score=random.randint(4, 9),
            anxiety_score=random.randint(2, 8),
            treatment_plan='Continue current treatment plan' if random.random() < 0.8 else 'Adjust medication',
            medications_prescribed='As prescribed' if random.random() < 0.7 else '',
            next_appointment_recommended=True,
            next_appointment_date=appointment.appointment_date + timedelta(days=random.randint(14, 30)),
            created_by=operator
        )
        sessions.append(session)
    
    print(f"✓ Created {len(sessions)} follow-up sessions")


def create_adherence_records(patients, appointments, users):
    """Create adherence records for patients."""
    print("\nCreating adherence records...")
    
    operator = users['operator2']
    records = []
    
    for patient in patients:
        patient_appointments = [a for a in appointments if a.patient == patient]
        
        if not patient_appointments:
            continue
        
        total = len(patient_appointments)
        attended = len([a for a in patient_appointments if a.status == 'COMPLETED'])
        missed = len([a for a in patient_appointments if a.status == 'MISSED'])
        
        adherence_rate = (attended / total * 100) if total > 0 else 0
        
        # Calculate consecutive missed
        recent_appointments = sorted(patient_appointments, key=lambda x: x.appointment_date, reverse=True)[:5]
        consecutive_missed = 0
        for appt in recent_appointments:
            if appt.status == 'MISSED':
                consecutive_missed += 1
            else:
                break
        
        if adherence_rate >= 80 and consecutive_missed == 0:
            risk_level = 'LOW'
        elif adherence_rate >= 60 and consecutive_missed <= 1:
            risk_level = 'MEDIUM'
        elif adherence_rate >= 40 or consecutive_missed <= 2:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'
        
        record = AdherenceRecord.objects.create(
            patient=patient,
            total_appointments=total,
            attended_appointments=attended,
            missed_appointments=missed,
            adherence_rate=Decimal(str(round(adherence_rate, 2))),
            consecutive_missed=consecutive_missed,
            risk_level=risk_level,
            notes=f'Adherence rate: {adherence_rate:.1f}%',
            created_by=operator
        )
        records.append(record)
    
    print(f"✓ Created {len(records)} adherence records")
    return records


def create_referral_actions(adherence_records, users):
    """Create referral actions for low adherence patients."""
    print("\nCreating referral actions...")
    
    supervisor = users['supervisor2']
    actions = []
    
    # Create referrals for HIGH and CRITICAL risk patients
    high_risk_records = [r for r in adherence_records if r.risk_level in ['HIGH', 'CRITICAL']]
    
    for record in high_risk_records:
        status = random.choice(['PENDING', 'COMPLETED'])
        
        action = ReferralAction.objects.create(
            patient=record.patient,
            action_type=random.choice(['REMINDER', 'FOLLOW_UP_CALL', 'HOME_VISIT']),
            status=status,
            trigger_reason=f'Low adherence rate ({record.adherence_rate}%)',
            action_date=date.today() - timedelta(days=random.randint(1, 14)),
            completed_date=date.today() - timedelta(days=random.randint(0, 7)) if status == 'COMPLETED' else None,
            assigned_to=supervisor,
            outcome='Patient contacted successfully' if status == 'COMPLETED' else '',
            created_by=supervisor
        )
        actions.append(action)
    
    print(f"✓ Created {len(actions)} referral actions")


def main():
    """Main function to generate all sample data."""
    print("=" * 70)
    print("GENERATING SAMPLE DATA FOR YOUTH SUPPORT PLATFORM")
    print("=" * 70)
    
    # Create users
    users = create_users()
    
    # Education scenario
    print("\n" + "=" * 70)
    print("SCENARIO 1: EDUCATION EARLY WARNING SYSTEM")
    print("=" * 70)
    students = create_students(users, count=30)
    create_attendance_records(students, users)
    create_grade_records(students, users)
    create_behavior_notes(students, users)
    assessments = create_risk_assessments(students, users)
    create_intervention_plans(assessments, users)
    
    # Health scenario
    print("\n" + "=" * 70)
    print("SCENARIO 2: HEALTH/MENTAL-HEALTH FOLLOW-UP")
    print("=" * 70)
    patients = create_patients(users, count=20)
    appointments = create_appointments(patients, users)
    create_follow_up_sessions(appointments, users)
    adherence_records = create_adherence_records(patients, appointments, users)
    create_referral_actions(adherence_records, users)
    
    print("\n" + "=" * 70)
    print("✅ SAMPLE DATA GENERATION COMPLETE!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  - Users: {User.objects.count()}")
    print(f"  - Students: {Student.objects.count()}")
    print(f"  - Attendance Records: {AttendanceRecord.objects.count()}")
    print(f"  - Grade Records: {GradeRecord.objects.count()}")
    print(f"  - Behavior Notes: {BehaviorNote.objects.count()}")
    print(f"  - Risk Assessments: {RiskAssessment.objects.count()}")
    print(f"  - Intervention Plans: {InterventionPlan.objects.count()}")
    print(f"  - Patients: {Patient.objects.count()}")
    print(f"  - Appointments: {Appointment.objects.count()}")
    print(f"  - Follow-up Sessions: {FollowUpSession.objects.count()}")
    print(f"  - Adherence Records: {AdherenceRecord.objects.count()}")
    print(f"  - Referral Actions: {ReferralAction.objects.count()}")
    print("\nYou can now:")
    print("  1. Login at http://127.0.0.1:8000/accounts/login/")
    print("  2. View dashboard at http://127.0.0.1:8000/dashboard/")
    print("  3. Test APIs at http://127.0.0.1:8000/api/docs/")
    print("  4. Use GraphQL at http://127.0.0.1:8000/graphql/")


if __name__ == '__main__':
    main()
