"""Add more students and patients - 10x multiplier"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_support_platform.settings')
import django
django.setup()

print("\n" + "="*70)
print("  MULTIPLYING DATASET BY 10X")
print("="*70)

# Run the existing script 10 times
for i in range(10):
    print(f"\n🔄 Batch {i+1}/10...")
    import subprocess
    result = subprocess.run(
        [r".\venv\Scripts\python.exe", "generate_sample_data.py"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"✅ Batch {i+1} complete")
    else:
        print(f"❌ Batch {i+1} failed")
        print(result.stderr[:200])

# Final count
from education.models import Student, AttendanceRecord, GradeRecord, RiskAssessment
from health.models import Patient, Appointment, AdherenceRecord

print("\n" + "="*70)
print("  FINAL STATISTICS")
print("="*70)
print(f"\n📚 EDUCATION:")
print(f"  - Students: {Student.objects.count()}")
print(f"  - Attendance: {AttendanceRecord.objects.count()}")
print(f"  - Grades: {GradeRecord.objects.count()}")
print(f"  - Risk Assessments: {RiskAssessment.objects.count()}")

print(f"\n🏥 HEALTH:")
print(f"  - Patients: {Patient.objects.count()}")
print(f"  - Appointments: {Appointment.objects.count()}")
print(f"  - Adherence Records: {AdherenceRecord.objects.count()}")

print("\n" + "="*70)
print("✅ Dataset multiplication complete!")
print("="*70 + "\n")
