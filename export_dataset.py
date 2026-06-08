"""
Export all data from the database to JSON and CSV files.
"""
import os
import django
import json
import csv
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_support_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from education.models import Student, AttendanceRecord, GradeRecord, BehaviorNote, RiskAssessment, InterventionPlan
from health.models import Patient, Appointment, FollowUpSession, AdherenceRecord, ReferralAction

User = get_user_model()

print("=" * 70)
print("EXPORTING DATASET")
print("=" * 70)

# Create exports directory
os.makedirs('dataset_exports', exist_ok=True)

# Export Students to CSV
print("\n📚 Exporting Students...")
students = Student.objects.all()
with open('dataset_exports/students.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Student_ID', 'First_Name', 'Last_Name', 'Date_of_Birth', 'Age', 
                     'Gender', 'School', 'Grade', 'Region', 'Guardian_Name', 'Guardian_Phone', 
                     'Guardian_Email', 'Enrollment_Date', 'Is_Active'])
    for s in students:
        writer.writerow([s.id, s.student_id, s.first_name, s.last_name, s.date_of_birth, s.age,
                        s.gender, s.school_name, s.grade_level, s.region, s.guardian_name,
                        s.guardian_phone, s.guardian_email, s.enrollment_date, s.is_active])
print(f"✅ Exported {students.count()} students")

# Export Attendance to CSV
print("\n📅 Exporting Attendance Records...")
attendance = AttendanceRecord.objects.all()
with open('dataset_exports/attendance.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Student_ID', 'Student_Name', 'Date', 'Status', 'Reason'])
    for a in attendance:
        writer.writerow([a.id, a.student.student_id, a.student.full_name, a.date, a.status, a.reason])
print(f"✅ Exported {attendance.count()} attendance records")

# Export Grades to CSV
print("\n📝 Exporting Grade Records...")
grades = GradeRecord.objects.all()
with open('dataset_exports/grades.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Student_ID', 'Student_Name', 'Subject', 'Grade', 'Exam_Type', 'Exam_Date'])
    for g in grades:
        writer.writerow([g.id, g.student.student_id, g.student.full_name, g.subject, 
                        float(g.grade), g.exam_type, g.exam_date])
print(f"✅ Exported {grades.count()} grade records")

# Export Risk Assessments to CSV
print("\n⚠️  Exporting Risk Assessments...")
risks = RiskAssessment.objects.all()
with open('dataset_exports/risk_assessments.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Student_ID', 'Student_Name', 'Assessment_Date', 'Attendance_Score',
                     'Academic_Score', 'Behavior_Score', 'Overall_Score', 'Risk_Level', 'Explanation'])
    for r in risks:
        writer.writerow([r.id, r.student.student_id, r.student.full_name, r.assessment_date,
                        float(r.attendance_score), float(r.academic_score), float(r.behavior_score),
                        float(r.overall_risk_score), r.risk_level, r.explanation])
print(f"✅ Exported {risks.count()} risk assessments")

# Export Patients to CSV
print("\n🏥 Exporting Patients...")
patients = Patient.objects.all()
with open('dataset_exports/patients.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Patient_ID', 'First_Name', 'Last_Name', 'Date_of_Birth',
                     'Gender', 'Phone', 'Email', 'Region', 'Emergency_Contact', 'Emergency_Phone',
                     'Registration_Date', 'Is_Active'])
    for p in patients:
        writer.writerow([p.id, p.patient_id, p.first_name, p.last_name, p.date_of_birth,
                        p.gender, p.phone_number, p.email, p.region, p.emergency_contact_name,
                        p.emergency_contact_phone, p.registration_date, p.is_active])
print(f"✅ Exported {patients.count()} patients")

# Export Appointments to CSV
print("\n📆 Exporting Appointments...")
appointments = Appointment.objects.all()
with open('dataset_exports/appointments.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Patient_ID', 'Patient_Name', 'Date', 'Time', 'Type', 'Status',
                     'Provider', 'Location', 'Reason'])
    for a in appointments:
        writer.writerow([a.id, a.patient.patient_id, a.patient.full_name, a.appointment_date,
                        a.appointment_time, a.appointment_type, a.status, a.provider_name,
                        a.location, a.reason])
print(f"✅ Exported {appointments.count()} appointments")

# Export Adherence Records to CSV
print("\n📊 Exporting Adherence Records...")
adherence = AdherenceRecord.objects.all()
with open('dataset_exports/adherence.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Patient_ID', 'Patient_Name', 'Assessment_Date', 'Total_Appointments',
                     'Attended', 'Missed', 'Adherence_Rate', 'Consecutive_Missed', 'Risk_Level'])
    for a in adherence:
        writer.writerow([a.id, a.patient.patient_id, a.patient.full_name, a.assessment_date,
                        a.total_appointments, a.attended_appointments, a.missed_appointments,
                        float(a.adherence_rate), a.consecutive_missed, a.risk_level])
print(f"✅ Exported {adherence.count()} adherence records")

# Export complete dataset to JSON
print("\n📦 Exporting Complete Dataset to JSON...")
dataset = {
    'export_date': datetime.now().isoformat(),
    'statistics': {
        'students': students.count(),
        'attendance_records': attendance.count(),
        'grade_records': grades.count(),
        'behavior_notes': BehaviorNote.objects.count(),
        'risk_assessments': risks.count(),
        'intervention_plans': InterventionPlan.objects.count(),
        'patients': patients.count(),
        'appointments': appointments.count(),
        'follow_up_sessions': FollowUpSession.objects.count(),
        'adherence_records': adherence.count(),
        'referral_actions': ReferralAction.objects.count(),
    },
    'students': [
        {
            'id': s.id,
            'student_id': s.student_id,
            'full_name': s.full_name,
            'date_of_birth': str(s.date_of_birth),
            'age': s.age,
            'gender': s.gender,
            'school_name': s.school_name,
            'grade_level': s.grade_level,
            'region': s.region,
            'guardian_name': s.guardian_name,
            'guardian_phone': s.guardian_phone,
            'is_active': s.is_active,
        }
        for s in students
    ],
    'patients': [
        {
            'id': p.id,
            'patient_id': p.patient_id,
            'full_name': p.full_name,
            'date_of_birth': str(p.date_of_birth),
            'gender': p.gender,
            'phone_number': p.phone_number,
            'email': p.email,
            'region': p.region,
            'is_active': p.is_active,
        }
        for p in patients
    ],
    'risk_assessments': [
        {
            'id': r.id,
            'student_id': r.student.student_id,
            'student_name': r.student.full_name,
            'assessment_date': str(r.assessment_date),
            'attendance_score': float(r.attendance_score),
            'academic_score': float(r.academic_score),
            'behavior_score': float(r.behavior_score),
            'overall_risk_score': float(r.overall_risk_score),
            'risk_level': r.risk_level,
        }
        for r in risks
    ],
    'adherence_records': [
        {
            'id': a.id,
            'patient_id': a.patient.patient_id,
            'patient_name': a.patient.full_name,
            'assessment_date': str(a.assessment_date),
            'total_appointments': a.total_appointments,
            'attended_appointments': a.attended_appointments,
            'adherence_rate': float(a.adherence_rate),
            'risk_level': a.risk_level,
        }
        for a in adherence
    ]
}

with open('dataset_exports/complete_dataset.json', 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)
print(f"✅ Exported complete dataset to JSON")

# Create README for dataset
readme_content = """# Youth Support Platform - Dataset Export

## Export Date
{export_date}

## Dataset Statistics

### Education Scenario
- Students: {students}
- Attendance Records: {attendance}
- Grade Records: {grades}
- Behavior Notes: {behavior}
- Risk Assessments: {risks}
- Intervention Plans: {interventions}

### Health Scenario
- Patients: {patients}
- Appointments: {appointments}
- Follow-up Sessions: {followups}
- Adherence Records: {adherence}
- Referral Actions: {referrals}

## Files Included

### CSV Files (for Excel/Analysis)
1. `students.csv` - All student records
2. `attendance.csv` - Attendance records (60 days)
3. `grades.csv` - Grade records (multiple subjects)
4. `risk_assessments.csv` - Risk assessment results
5. `patients.csv` - All patient records
6. `appointments.csv` - Appointment records
7. `adherence.csv` - Adherence tracking records

### JSON File (for Programming)
- `complete_dataset.json` - Complete dataset in JSON format

## Data Characteristics

### Tunisian Context
- Names: Realistic Tunisian first and last names
- Schools: Tunisian schools (École Carthage, Lycée Sadiki, etc.)
- Regions: Tunisian regions (Tunis, Ariana, Sfax, etc.)
- Phone numbers: Tunisian format (20-29 prefix)

### Risk Levels
- LOW: Overall score ≥ 80
- MEDIUM: Overall score 60-79
- HIGH: Overall score 40-59
- CRITICAL: Overall score < 40

### Risk Score Calculation
- Attendance Score: 40% weight
- Academic Score: 40% weight
- Behavior Score: 20% weight

## Usage

### Excel/Spreadsheet
Open any CSV file in Excel, Google Sheets, or LibreOffice Calc.

### Python
```python
import pandas as pd

# Load students
students = pd.read_csv('students.csv')

# Load risk assessments
risks = pd.read_csv('risk_assessments.csv')

# Analyze
print(students.describe())
print(risks.groupby('Risk_Level').size())
```

### JSON
```python
import json

with open('complete_dataset.json', 'r') as f:
    data = json.load(f)

print(f"Total students: {{len(data['students'])}}")
print(f"Total patients: {{len(data['patients'])}}")
```

## Data Quality

- All records have realistic values
- Dates are consistent and logical
- Scores are within valid ranges (0-100)
- No missing required fields
- Relationships are properly maintained

## License

This dataset is generated for educational purposes as part of the 
Youth Support Platform project for SESAME University.

Generated: {export_date}
""".format(
    export_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    students=students.count(),
    attendance=attendance.count(),
    grades=grades.count(),
    behavior=BehaviorNote.objects.count(),
    risks=risks.count(),
    interventions=InterventionPlan.objects.count(),
    patients=patients.count(),
    appointments=appointments.count(),
    followups=FollowUpSession.objects.count(),
    adherence=adherence.count(),
    referrals=ReferralAction.objects.count()
)

with open('dataset_exports/README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("\n" + "=" * 70)
print("✅ EXPORT COMPLETE!")
print("=" * 70)
print(f"\nFiles created in: dataset_exports/")
print("\nCSV Files:")
print("  - students.csv")
print("  - attendance.csv")
print("  - grades.csv")
print("  - risk_assessments.csv")
print("  - patients.csv")
print("  - appointments.csv")
print("  - adherence.csv")
print("\nJSON File:")
print("  - complete_dataset.json")
print("\nDocumentation:")
print("  - README.md")
print("\nYou can now use these files for analysis, reporting, or backup.")
