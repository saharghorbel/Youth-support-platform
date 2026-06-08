# Dataset Exports - Youth Support Platform

**Export Date:** 2026-06-06 12:21:38

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
- Students: 30
- Attendance Records: 1290
- Grades: 374
- Behaviors: 24
- Risk Assessments: 30
- Interventions: 0

**Health:**
- Patients: 20
- Appointments: 103
- Follow-ups: 40
- Adherence Records: 20
- Referrals: 12

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
