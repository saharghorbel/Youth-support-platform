"""
Generate LARGE synthetic dataset for Youth Support Platform
Creates 500+ students and 500+ patients with all associated records
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
    BehaviorNote, RiskAssessment, InterventionPlan, RiskThreshold
)
from health.models import (
    Patient, Appointment, FollowUpSession,
    AdherenceRecord, ReferralAction
)

User = get_user_model()

# Configuration
NUM_STUDENTS = 500
NUM_PATIENTS = 500

# Sample data
TUNISIAN_FIRST_NAMES_MALE = [
    'Mohamed', 'Ahmed', 'Ali', 'Youssef', 'Mehdi', 'Amine', 'Karim', 'Rami',
    'Sami', 'Tarek', 'Walid', 'Zied', 'Hamza', 'Bilel', 'Fares', 'Nabil',
    'Hichem', 'Anis', 'Maher', 'Samir', 'Fadi', 'Khalil', 'Omar', 'Hatem'
]

TUNISIAN_FIRST_NAMES_FEMALE = [
    'Fatma', 'Amira', 'Salma', 'Nour', 'Ines', 'Mariem', 'Yasmine', 'Leila',
    'Sarra', 'Rim', 'Hiba', 'Dorra', 'Emna', 'Nesrine', 'Rahma', 'Asma',
    'Wafa', 'Hana', 'Sihem', 'Latifa', 'Meriem', 'Soumaya', 'Naima'
]

TUNISIAN_LAST_NAMES = [
    'Ben Ali', 'Trabelsi', 'Gharbi', 'Jebali', 'Mansouri', 'Bouazizi',
    'Hamdi', 'Karoui', 'Mejri', 'Sassi', 'Dridi', 'Chouchane', 'Oueslati',
    'Bouzid', 'Khelifi', 'Maaloul', 'Slimani', 'Ayari', 'Belhadj', 'Chaabane',
    'Ferchichi', 'Mrad', 'Zaidi', 'Chatti', 'Ghanmi', 'Hammami', 'Jouini'
]

SCHOOLS = [
    'Collège Ibn Khaldoun', 'Lycée Bourguiba Sfax', 'École Primaire Carthage',
    'Lycée Pilote Ariana', 'Collège Sadiki', 'École El Manar Tunis',
    'Lycée Pierre Mendès France', 'Collège La Marsa', 'École Menzah 6',
    'Lycée Habib Thameur', 'Collège Hannibal', 'École Bardo',
    'Lycée Averroès', 'Collège Cité Olympique', 'École Manar 2'
]

REGIONS = [
    'Tunis', 'Ariana', 'Ben Arous', 'Manouba', 'Sfax', 'Sousse',
    'Nabeul', 'Bizerte', 'Gabès', 'Kairouan', 'Monastir', 'Mahdia'
]

SUBJECTS = ['Mathematics', 'Physics', 'Arabic', 'French', 'English', 'Science', 'History', 'Geography']

BEHAVIOR_TYPES = ['POSITIVE', 'NEUTRAL', 'NEGATIVE', 'SEVERE']

def random_date(start_date, end_date):
    """Generate random date between start and end"""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_phone():
    """Generate random Tunisian phone number"""
    prefixes = ['20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
                '50', '51', '52', '53', '54', '55', '56', '57', '58', '59',
                '90', '91', '92', '93', '94', '95', '96', '97', '98', '99']
    prefix = random.choice(prefixes)
    number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    formatted = f"{number[:3]} {number[3:]}"
    return f"+216 {prefix} {formatted}"

def generate_students(num_students):
    """Generate students with all related data"""
    print(f"\n{'='*70}")
    print(f"Generating {num_students} students...")
    print(f"{'='*70}")
    
    operator = User.objects.filter(role='OPERATOR').first()
    supervisor = User.objects.filter(role='SUPERVISOR').first()
    
    students_created = 0
    
    for i in range(num_students):
        # Create student
        gender = random.choice(['M', 'F'])
        first_names = TUNISIAN_FIRST_NAMES_MALE if gender == 'M' else TUNISIAN_FIRST_NAMES_FEMALE
        first_name = random.choice(first_names)
        last_name = random.choice(TUNISIAN_LAST_NAMES)
        
        birth_year = random.randint(2006, 2018)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
        student = Student.objects.create(
            student_id=f"STU{2026:04d}{(i+1):04d}",
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date(birth_year, birth_month, birth_day),
            gender=gender,
            school_name=random.choice(SCHOOLS),
            grade_level=random.randint(1, 12),
            region=random.choice(REGIONS),
            guardian_name=f"{random.choice(TUNISIAN_FIRST_NAMES_MALE)} {last_name}",
            guardian_phone=random_phone(),
            guardian_email=f"{last_name.lower().replace(' ', '_')}@example.tn",
            enrollment_date=random_date(date(2025, 9, 1), date(2026, 1, 1)),
            is_active=random.random() > 0.1,
            created_by=operator
        )
        
        # Generate attendance records (30-180 records per student)
        num_attendance = random.randint(30, 180)
        for _ in range(num_attendance):
            AttendanceRecord.objects.create(
                student=student,
                date=random_date(date(2025, 9, 1), date(2026, 5, 30)),
                status=random.choices(['PRESENT', 'ABSENT', 'LATE', 'EXCUSED'],
                                     weights=[70, 15, 10, 5])[0],
                notes=random.choice(['', '', '', 'Malade', 'Raison familiale', '']) if random.random() > 0.8 else '',
                created_by=operator
            )
        
        # Generate grade records (10-30 per student)
        num_grades = random.randint(10, 30)
        for _ in range(num_grades):
            GradeRecord.objects.create(
                student=student,
                subject=random.choice(SUBJECTS),
                grade=round(random.uniform(3, 20), 2),
                max_grade=20,
                exam_date=random_date(date(2025, 10, 1), date(2026, 5, 15)),
                exam_type=random.choice(['QUIZ', 'MIDTERM', 'FINAL', 'HOMEWORK']),
                notes='',
                created_by=operator
            )
        
        # Generate behavior notes (0-8 per student)
        if random.random() > 0.3:
            num_behavior = random.randint(0, 8)
            for _ in range(num_behavior):
                BehaviorNote.objects.create(
                    student=student,
                    date=random_date(date(2025, 9, 1), date(2026, 5, 30)),
                    behavior_type=random.choices(BEHAVIOR_TYPES, weights=[20, 40, 30, 10])[0],
                    description=random.choice([
                        'Participation active en classe',
                        'Bon comportement',
                        'Perturbation en classe',
                        'Absences répétées',
                        'Aide aux autres élèves',
                        'Manque de concentration',
                        'Excellence académique',
                        'Comportement agressif'
                    ]),
                    action_taken=random.choice(['', 'Avertissement', 'Convocation parents', 'Félicitations']),
                    created_by=operator
                )
        
        # Generate risk assessments (1-5 per student)
        num_assessments = random.randint(1, 5)
        for _ in range(num_assessments):
            attendance_score = round(random.uniform(30, 100), 2)
            grade_score = round(random.uniform(30, 100), 2)
            behavior_score = round(random.uniform(30, 100), 2)
            social_score = round(random.uniform(30, 100), 2)
            
            overall_score = (attendance_score + grade_score + behavior_score + social_score) / 4
            
            if overall_score < 40:
                risk_level = 'CRITICAL'
            elif overall_score < 55:
                risk_level = 'HIGH'
            elif overall_score < 70:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            assessment = RiskAssessment.objects.create(
                student=student,
                assessment_date=random_date(date(2025, 10, 1), date(2026, 5, 25)),
                attendance_score=attendance_score,
                grade_score=grade_score,
                behavior_score=behavior_score,
                social_score=social_score,
                overall_risk_score=round(overall_score, 2),
                risk_level=risk_level,
                notes=f"Évaluation {risk_level.lower()}",
                assessed_by=supervisor,
                created_by=supervisor
            )
            
            # Generate intervention plan if high risk
            if risk_level in ['HIGH', 'CRITICAL'] and random.random() > 0.3:
                InterventionPlan.objects.create(
                    student=student,
                    risk_assessment=assessment,
                    plan_type=random.choice(['ACADEMIC', 'BEHAVIORAL', 'SOCIAL', 'COMPREHENSIVE']),
                    description=f"Plan d'intervention pour niveau {risk_level}",
                    goals="Améliorer la performance et le comportement",
                    planned_start_date=assessment.assessment_date + timedelta(days=random.randint(1, 7)),
                    planned_end_date=assessment.assessment_date + timedelta(days=random.randint(30, 90)),
                    status=random.choice(['PENDING', 'APPROVED', 'IN_PROGRESS', 'COMPLETED']),
                    assigned_to=supervisor,
                    created_by=supervisor
                )
        
        students_created += 1
        if (i + 1) % 50 == 0:
            print(f"  ✅ {i + 1}/{num_students} students created...")
    
    print(f"\n✅ Created {students_created} students with all records")
    return students_created

def generate_patients(num_patients):
    """Generate patients with all related data"""
    print(f"\n{'='*70}")
    print(f"Generating {num_patients} patients...")
    print(f"{'='*70}")
    
    operator = User.objects.filter(role='OPERATOR').first()
    supervisor = User.objects.filter(role='SUPERVISOR').first()
    
    patients_created = 0
    
    for i in range(num_patients):
        # Create patient
        gender = random.choice(['M', 'F'])
        first_names = TUNISIAN_FIRST_NAMES_MALE if gender == 'M' else TUNISIAN_FIRST_NAMES_FEMALE
        first_name = random.choice(first_names)
        last_name = random.choice(TUNISIAN_LAST_NAMES)
        
        birth_year = random.randint(2006, 2020)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
        patient = Patient.objects.create(
            patient_id=f"PAT{2026:04d}{(i+1):04d}",
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date(birth_year, birth_month, birth_day),
            gender=gender,
            phone_number=random_phone(),
            email=f"{first_name.lower()}.{last_name.lower().replace(' ', '_')}@example.tn" if random.random() > 0.5 else '',
            address=f"{random.randint(1, 200)} Rue {random.choice(['Bourguiba', 'Carthage', 'Hannibal', 'Ibn Khaldoun'])}",
            region=random.choice(REGIONS),
            emergency_contact_name=f"{random.choice(TUNISIAN_FIRST_NAMES_MALE)} {last_name}",
            emergency_contact_phone=random_phone(),
            registration_date=random_date(date(2025, 1, 1), date(2026, 3, 1)),
            is_active=random.random() > 0.1,
            medical_notes=random.choice(['', '', '', 'Suivi régulier', 'Traitement en cours']) if random.random() > 0.7 else '',
            created_by=operator
        )
        
        # Generate appointments (5-30 per patient)
        num_appointments = random.randint(5, 30)
        for _ in range(num_appointments):
            appt_date = random_date(date(2025, 1, 1), date(2026, 5, 30))
            Appointment.objects.create(
                patient=patient,
                appointment_date=appt_date,
                appointment_time=time(random.randint(8, 17), random.choice([0, 30])),
                appointment_type=random.choice(['CONSULTATION', 'FOLLOW_UP', 'EMERGENCY', 'SCREENING']),
                status=random.choices(['SCHEDULED', 'CONFIRMED', 'COMPLETED', 'MISSED', 'CANCELLED'],
                                     weights=[10, 15, 50, 15, 10])[0],
                notes='',
                created_by=operator
            )
        
        # Generate follow-up sessions (3-15 per patient)
        num_followups = random.randint(3, 15)
        for _ in range(num_followups):
            FollowUpSession.objects.create(
                patient=patient,
                session_date=random_date(date(2025, 2, 1), date(2026, 5, 25)),
                session_type=random.choice(['COUNSELING', 'MEDICAL', 'SOCIAL', 'EDUCATIONAL']),
                notes=random.choice(['Progrès satisfaisant', 'Nécessite suivi', 'Bon état', '']),
                recommendations='',
                conducted_by=supervisor,
                created_by=supervisor
            )
        
        # Generate adherence records (2-10 per patient)
        num_adherence = random.randint(2, 10)
        for _ in range(num_adherence):
            adherence_rate = round(random.uniform(40, 100), 2)
            
            if adherence_rate >= 85:
                risk_level = 'LOW'
            elif adherence_rate >= 70:
                risk_level = 'MEDIUM'
            elif adherence_rate >= 50:
                risk_level = 'HIGH'
            else:
                risk_level = 'CRITICAL'
            
            AdherenceRecord.objects.create(
                patient=patient,
                assessment_date=random_date(date(2025, 2, 1), date(2026, 5, 25)),
                adherence_rate=adherence_rate,
                missed_appointments=random.randint(0, 5),
                risk_level=risk_level,
                notes='',
                assessed_by=supervisor,
                created_by=supervisor
            )
        
        # Generate referral actions (0-5 per patient)
        if random.random() > 0.4:
            num_referrals = random.randint(0, 5)
            for _ in range(num_referrals):
                ReferralAction.objects.create(
                    patient=patient,
                    action_date=random_date(date(2025, 3, 1), date(2026, 5, 20)),
                    action_type=random.choice(['REFERRAL', 'FOLLOWUP', 'ESCALATION', 'CLOSURE']),
                    description=random.choice([
                        'Référence au service social',
                        'Suivi médical spécialisé',
                        'Soutien psychologique',
                        'Aide financière'
                    ]),
                    status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
                    performed_by=supervisor,
                    created_by=supervisor
                )
        
        patients_created += 1
        if (i + 1) % 50 == 0:
            print(f"  ✅ {i + 1}/{num_patients} patients created...")
    
    print(f"\n✅ Created {patients_created} patients with all records")
    return patients_created

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("  YOUTH SUPPORT PLATFORM - LARGE DATASET GENERATOR")
    print("="*70)
    
    print(f"\nConfiguration:")
    print(f"  - Students to create: {NUM_STUDENTS}")
    print(f"  - Patients to create: {NUM_PATIENTS}")
    print(f"  - Total expected: {NUM_STUDENTS + NUM_PATIENTS} individuals")
    
    input("\nPress Enter to start generation...")
    
    # Generate data
    students = generate_students(NUM_STUDENTS)
    patients = generate_patients(NUM_PATIENTS)
    
    # Summary
    print("\n" + "="*70)
    print("  GENERATION COMPLETE")
    print("="*70)
    
    total_students = Student.objects.count()
    total_patients = Patient.objects.count()
    total_attendance = AttendanceRecord.objects.count()
    total_grades = GradeRecord.objects.count()
    total_behaviors = BehaviorNote.objects.count()
    total_risk_assessments = RiskAssessment.objects.count()
    total_interventions = InterventionPlan.objects.count()
    total_appointments = Appointment.objects.count()
    total_followups = FollowUpSession.objects.count()
    total_adherence = AdherenceRecord.objects.count()
    total_referrals = ReferralAction.objects.count()
    
    print(f"\n📊 EDUCATION MODULE:")
    print(f"  - Students: {total_students}")
    print(f"  - Attendance Records: {total_attendance}")
    print(f"  - Grade Records: {total_grades}")
    print(f"  - Behavior Notes: {total_behaviors}")
    print(f"  - Risk Assessments: {total_risk_assessments}")
    print(f"  - Intervention Plans: {total_interventions}")
    
    print(f"\n🏥 HEALTH MODULE:")
    print(f"  - Patients: {total_patients}")
    print(f"  - Appointments: {total_appointments}")
    print(f"  - Follow-up Sessions: {total_followups}")
    print(f"  - Adherence Records: {total_adherence}")
    print(f"  - Referral Actions: {total_referrals}")
    
    total_records = (total_attendance + total_grades + total_behaviors + 
                    total_risk_assessments + total_interventions + total_appointments +
                    total_followups + total_adherence + total_referrals)
    
    print(f"\n📈 TOTALS:")
    print(f"  - Total Individuals: {total_students + total_patients}")
    print(f"  - Total Records: {total_records}")
    
    print("\n✅ Large dataset generated successfully!")
    print("="*70)

if __name__ == '__main__':
    main()
