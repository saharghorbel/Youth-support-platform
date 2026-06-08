"""
Export all database data to CSV files
Creates comprehensive CSV exports of all tables
"""
import os
import django
import csv
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_support_platform.settings')
django.setup()

from education.models import (
    Student, AttendanceRecord, GradeRecord,
    BehaviorNote, RiskAssessment, InterventionPlan
)
from health.models import (
    Patient, Appointment, FollowUpSession,
    AdherenceRecord, ReferralAction
)

# Create export directory if it doesn't exist
EXPORT_DIR = 'dataset_exports'
os.makedirs(EXPORT_DIR, exist_ok=True)

print("\n" + "="*70)
print("  EXPORTING ALL DATA TO CSV FILES")
print("="*70)

def export_students():
    """Export students to CSV"""
    filename = os.path.join(EXPORT_DIR, 'students.csv')
    students = Student.objects.all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Student ID', 'First Name', 'Last Name', 'Date of Birth', 
            'Gender', 'School Name', 'Grade Level', 'Region', 
            'Guardian Name', 'Guardian Phone', 'Guardian Email',
            'Enrollment Date', 'Is Active'
        ])
        
        for student in students:
            writer.writerow([
                student.id,
                student.student_id,
                student.first_name,
                student.last_name,
                student.date_of_birth,
                student.gender,
                student.school_name,
                student.grade_level,
                student.region,
                student.guardian_name,
                student.guardian_phone,
                student.guardian_email,
                student.enrollment_date,
                student.is_active
            ])
    
    print(f"✅ Exported {students.count()} students to {filename}")

def export_attendance():
    """Export attendance records to CSV"""
    filename = os.path.join(EXPORT_DIR, 'attendance.csv')
    records = AttendanceRecord.objects.select_related('student').all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Student ID', 'Student Name', 'Date', 'Status', 'Reason'
        ])
        
        for record in records:
            writer.writerow([
                record.id,
                record.student.student_id,
                f"{record.student.first_name} {record.student.last_name}",
                record.date,
                record.status,
                record.reason or ''
            ])
    
    print(f"✅ Exported {records.count()} attendance records to {filename}")

def export_grades():
    """Export grades to CSV"""
    filename = os.path.join(EXPORT_DIR, 'grades.csv')
    grades = GradeRecord.objects.select_related('student').all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Student ID', 'Student Name', 'Subject', 'Grade', 
            'Exam Date', 'Exam Type', 'Comments'
        ])
        
        for grade in grades:
            writer.writerow([
                grade.id,
                grade.student.student_id,
                f"{grade.student.first_name} {grade.student.last_name}",
                grade.subject,
                grade.grade,
                grade.exam_date,
                grade.exam_type,
                grade.comments or ''
            ])
    
    print(f"✅ Exported {grades.count()} grades to {filename}")

def export_behaviors():
    """Export behavior notes to CSV"""
    filename = os.path.join(EXPORT_DIR, 'behaviors.csv')
    behaviors = BehaviorNote.objects.select_related('student').all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Student ID', 'Student Name', 'Date', 'Severity', 'Category',
            'Description', 'Action Taken'
        ])
        
        for behavior in behaviors:
            writer.writerow([
                behavior.id,
                behavior.student.student_id,
                f"{behavior.student.first_name} {behavior.student.last_name}",
                behavior.date,
                behavior.severity,
                behavior.category,
                behavior.description,
                behavior.action_taken or ''
            ])
    
    print(f"✅ Exported {behaviors.count()} behavior notes to {filename}")

def export_risk_assessments():
    """Export risk assessments to CSV"""
    filename = os.path.join(EXPORT_DIR, 'risk_assessments.csv')
    assessments = RiskAssessment.objects.select_related('student').all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Student ID', 'Student Name', 'Assessment Date',
            'Attendance Score', 'Academic Score', 'Behavior Score',
            'Overall Risk Score', 'Risk Level', 'Explanation', 'Recommendations'
        ])
        
        for assessment in assessments:
            writer.writerow([
                assessment.id,
                assessment.student.student_id,
                f"{assessment.student.first_name} {assessment.student.last_name}",
                assessment.assessment_date,
                assessment.attendance_score,
                assessment.academic_score,
                assessment.behavior_score,
                assessment.overall_risk_score,
                assessment.risk_level,
                assessment.explanation,
                assessment.recommendations
            ])
    
    print(f"✅ Exported {assessments.count()} risk assessments to {filename}")

def export_interventions():
    """Export intervention plans to CSV"""
    filename = os.path.join(EXPORT_DIR, 'interventions.csv')
    interventions = InterventionPlan.objects.select_related('student').all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Student ID', 'Student Name', 'Title', 'Description',
            'Status', 'Start Date', 'Target End Date', 'Goals', 'Actions'
        ])
        
        for intervention in interventions:
            writer.writerow([
                intervention.id,
                intervention.student.student_id,
                f"{intervention.student.first_name} {intervention.student.last_name}",
                intervention.title,
                intervention.description,
                intervention.status,
                intervention.start_date,
                intervention.target_end_date,
                intervention.goals,
                intervention.actions
            ])
    
    print(f"✅ Exported {interventions.count()} interventions to {filename}")

def export_patients():
    """Export patients to CSV"""
    filename = os.path.join(EXPORT_DIR, 'patients.csv')
    patients = Patient.objects.all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Patient ID', 'First Name', 'Last Name', 'Date of Birth',
            'Gender', 'Phone', 'Email', 'Address', 'Region',
            'Emergency Contact Name', 'Emergency Contact Phone',
            'Registration Date', 'Is Active'
        ])
        
        for patient in patients:
            writer.writerow([
                patient.id,
                patient.patient_id,
                patient.first_name,
                patient.last_name,
                patient.date_of_birth,
                patient.gender,
                patient.phone_number,
                patient.email or '',
                patient.address or '',
                patient.region,
                patient.emergency_contact_name,
                patient.emergency_contact_phone,
                patient.registration_date,
                patient.is_active
            ])
    
    print(f"✅ Exported {patients.count()} patients to {filename}")

def export_appointments():
    """Export appointments to CSV"""
    filename = os.path.join(EXPORT_DIR, 'appointments.csv')
    appointments = Appointment.objects.select_related('patient').all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Patient ID', 'Patient Name', 'Appointment Date',
            'Appointment Time', 'Type', 'Status', 'Notes'
        ])
        
        for appointment in appointments:
            writer.writerow([
                appointment.id,
                appointment.patient.patient_id,
                f"{appointment.patient.first_name} {appointment.patient.last_name}",
                appointment.appointment_date,
                appointment.appointment_time,
                appointment.appointment_type,
                appointment.status,
                appointment.notes or ''
            ])
    
    print(f"✅ Exported {appointments.count()} appointments to {filename}")

def export_followups():
    """Export follow-up sessions to CSV"""
    filename = os.path.join(EXPORT_DIR, 'followups.csv')
    followups = FollowUpSession.objects.select_related('patient').all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Patient ID', 'Patient Name', 'Session Date',
            'Duration (min)', 'Provider', 'Mood Score', 'Anxiety Score',
            'Symptoms', 'Assessment Notes', 'Treatment Plan'
        ])
        
        for followup in followups:
            writer.writerow([
                followup.id,
                followup.patient.patient_id,
                f"{followup.patient.first_name} {followup.patient.last_name}",
                followup.session_date,
                followup.session_duration,
                followup.provider_name,
                followup.mood_score,
                followup.anxiety_score,
                followup.symptoms_reported,
                followup.assessment_notes,
                followup.treatment_plan
            ])
    
    print(f"✅ Exported {followups.count()} follow-ups to {filename}")

def export_adherence():
    """Export adherence records to CSV"""
    filename = os.path.join(EXPORT_DIR, 'adherence.csv')
    records = AdherenceRecord.objects.select_related('patient').all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Patient ID', 'Patient Name', 'Assessment Date',
            'Adherence Rate', 'Missed Appointments', 'Risk Level', 'Notes'
        ])
        
        for record in records:
            writer.writerow([
                record.id,
                record.patient.patient_id,
                f"{record.patient.first_name} {record.patient.last_name}",
                record.assessment_date,
                record.adherence_rate,
                record.missed_appointments,
                record.risk_level,
                record.notes or ''
            ])
    
    print(f"✅ Exported {records.count()} adherence records to {filename}")

def export_referrals():
    """Export referral actions to CSV"""
    filename = os.path.join(EXPORT_DIR, 'referrals.csv')
    referrals = ReferralAction.objects.select_related('patient').all()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Patient ID', 'Patient Name', 'Action Date',
            'Action Type', 'Status', 'Trigger Reason', 'Outcome'
        ])
        
        for referral in referrals:
            writer.writerow([
                referral.id,
                referral.patient.patient_id,
                f"{referral.patient.first_name} {referral.patient.last_name}",
                referral.action_date,
                referral.action_type,
                referral.status,
                referral.trigger_reason,
                referral.outcome or ''
            ])
    
    print(f"✅ Exported {referrals.count()} referrals to {filename}")

def create_readme():
    """Create README for the exports"""
    filename = os.path.join(EXPORT_DIR, 'README.md')
    
    content = f"""# Dataset Exports - Youth Support Platform

**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📁 Files Included

### 📚 Education Module
- `students.csv` - Student information
- `attendance.csv` - Attendance records
- `grades.csv` - Grade records
- `behaviors.csv` - Behavior notes
- `risk_assessments.csv` - Risk assessments
- `interventions.csv` - Intervention plans

### 🏥 Health Module
- `patients.csv` - Patient information
- `appointments.csv` - Appointment records
- `followups.csv` - Follow-up sessions
- `adherence.csv` - Adherence records
- `referrals.csv` - Referral actions

## 📊 Statistics

**Education:**
- Students: {Student.objects.count()}
- Attendance Records: {AttendanceRecord.objects.count()}
- Grades: {GradeRecord.objects.count()}
- Behaviors: {BehaviorNote.objects.count()}
- Risk Assessments: {RiskAssessment.objects.count()}
- Interventions: {InterventionPlan.objects.count()}

**Health:**
- Patients: {Patient.objects.count()}
- Appointments: {Appointment.objects.count()}
- Follow-ups: {FollowUpSession.objects.count()}
- Adherence Records: {AdherenceRecord.objects.count()}
- Referrals: {ReferralAction.objects.count()}

## 💾 File Format

All files are in CSV format with UTF-8 encoding:
- Delimiter: comma (`,`)
- Encoding: UTF-8
- Line ending: CRLF (Windows)

## 🔄 Regenerate Exports

To regenerate these files:

```bash
python export_all_to_csv.py
```

## 📝 Notes

- All dates are in YYYY-MM-DD format
- Times are in HH:MM:SS format
- Empty fields are represented as empty strings
- Boolean values: True/False

---

**Youth Support Platform**  
Exam Project - Django 2026
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created README.md")

def main():
    """Main execution"""
    try:
        # Export all data
        print("\n📚 EDUCATION MODULE:")
        export_students()
        export_attendance()
        export_grades()
        export_behaviors()
        export_risk_assessments()
        export_interventions()
        
        print("\n🏥 HEALTH MODULE:")
        export_patients()
        export_appointments()
        export_followups()
        export_adherence()
        export_referrals()
        
        print("\n📄 DOCUMENTATION:")
        create_readme()
        
        print("\n" + "="*70)
        print("✅ ALL DATA EXPORTED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📁 Files saved in: {EXPORT_DIR}/")
        print("\nYou can now:")
        print("  - Open CSV files in Excel/LibreOffice")
        print("  - Import data into other systems")
        print("  - Analyze data with pandas/R")
        print("  - Share the dataset")
        
    except Exception as e:
        print(f"\n❌ Error during export: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
