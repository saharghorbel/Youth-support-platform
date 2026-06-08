"""
Dashboard views for monitoring and reporting.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from education.models import Student, RiskAssessment, InterventionPlan
from health.models import Patient, Appointment
from accounts.models import AuditLog


@login_required
def home(request):
    """Main dashboard view with KPIs and overview."""
    
    # Calculate KPIs
    total_students = Student.objects.filter(is_active=True).count()
    
    # Get risk assessments from last 30 days
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_assessments = RiskAssessment.objects.filter(
        assessment_date__gte=thirty_days_ago
    )
    
    high_risk_count = recent_assessments.filter(
        risk_level__in=['HIGH', 'CRITICAL']
    ).values('student').distinct().count()
    
    active_interventions = InterventionPlan.objects.filter(
        status__in=['APPROVED', 'IN_PROGRESS']
    ).count()
    
    # Calculate completion rate
    completed_interventions = InterventionPlan.objects.filter(
        status='COMPLETED',
        actual_end_date__gte=thirty_days_ago
    ).count()
    
    total_interventions = InterventionPlan.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    completion_rate = (
        (completed_interventions / total_interventions * 100)
        if total_interventions > 0 else 0
    )
    
    # Risk distribution
    risk_distribution = {
        'low': recent_assessments.filter(risk_level='LOW').count(),
        'medium': recent_assessments.filter(risk_level='MEDIUM').count(),
        'high': recent_assessments.filter(risk_level='HIGH').count(),
        'critical': recent_assessments.filter(risk_level='CRITICAL').count(),
    }
    
    # Critical alerts
    critical_alerts = RiskAssessment.objects.filter(
        risk_level='CRITICAL',
        assessment_date__gte=thirty_days_ago
    ).select_related('student').order_by('-assessment_date')[:5]
    
    # Recent activity
    recent_activities = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    # Pending interventions
    pending_interventions = InterventionPlan.objects.filter(
        status='PENDING'
    ).select_related('student', 'assigned_to', 'risk_assessment').order_by('-created_at')[:10]
    
    # System health metrics
    total_records = Student.objects.count() + Patient.objects.count()
    valid_records = Student.objects.filter(is_active=True).count()
    data_quality = (valid_records / total_records * 100) if total_records > 0 else 100
    
    workflow_completion = completion_rate
    
    context = {
        'kpis': {
            'total_students': total_students,
            'high_risk_count': high_risk_count,
            'active_interventions': active_interventions,
            'completion_rate': round(completion_rate, 1),
        },
        'risk_distribution': risk_distribution,
        'critical_alerts': critical_alerts,
        'recent_activities': recent_activities,
        'pending_interventions': pending_interventions,
        'system_health': {
            'data_quality': round(data_quality, 1),
            'workflow_completion': round(workflow_completion, 1),
            'response_time': 45,  # Mock value
        }
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def alerts(request):
    """View all alerts and risk assessments."""
    
    # Filter by risk level
    risk_level = request.GET.get('risk_level', '')
    
    assessments = RiskAssessment.objects.select_related('student').order_by('-assessment_date')
    
    if risk_level:
        assessments = assessments.filter(risk_level=risk_level)
    
    # Statistics
    stats = {
        'total': assessments.count(),
        'critical': assessments.filter(risk_level='CRITICAL').count(),
        'high': assessments.filter(risk_level='HIGH').count(),
        'medium': assessments.filter(risk_level='MEDIUM').count(),
        'low': assessments.filter(risk_level='LOW').count(),
    }
    
    context = {
        'assessments': assessments[:50],  # Limit to 50 for performance
        'stats': stats,
        'current_filter': risk_level,
    }
    
    return render(request, 'dashboard/alerts.html', context)


@login_required
def reports(request):
    """Generate and view reports with export functionality."""
    from health.models import AdherenceRecord, ReferralAction
    
    # Date range filter
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # KPI Summary
    total_students = Student.objects.filter(is_active=True).count()
    total_patients = Patient.objects.filter(is_active=True).count()
    
    # High risk count
    recent_assessments = RiskAssessment.objects.filter(assessment_date__gte=start_date)
    high_risk_count = recent_assessments.filter(risk_level__in=['HIGH', 'CRITICAL']).values('student').distinct().count()
    
    # Pending alerts (referral actions)
    pending_alerts = ReferralAction.objects.filter(status='PENDING').count()
    
    # Recent audit logs (last 20)
    recent_audit_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:20]
    
    # Workflow completion metrics
    total_students_enrolled = Student.objects.count()
    completed_students = Student.objects.filter(is_active=False).count()
    student_completion_rate = (completed_students / total_students_enrolled * 100) if total_students_enrolled > 0 else 0
    
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status='COMPLETED').count()
    appointment_completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
    
    total_interventions = InterventionPlan.objects.count()
    completed_interventions = InterventionPlan.objects.filter(status='COMPLETED').count()
    intervention_completion_rate = (completed_interventions / total_interventions * 100) if total_interventions > 0 else 0
    
    workflow_metrics = {
        'student_completion_rate': round(student_completion_rate, 1),
        'appointment_completion_rate': round(appointment_completion_rate, 1),
        'intervention_completion_rate': round(intervention_completion_rate, 1),
    }
    
    context = {
        'days': days,
        'start_date': start_date,
        'total_students': total_students,
        'total_patients': total_patients,
        'high_risk_count': high_risk_count,
        'pending_alerts': pending_alerts,
        'recent_audit_logs': recent_audit_logs,
        'workflow_metrics': workflow_metrics,
    }
    
    return render(request, 'dashboard/reports.html', context)


@login_required
def kpis_api(request):
    """API endpoint for KPIs (for AJAX updates)."""
    from django.http import JsonResponse
    
    total_students = Student.objects.filter(is_active=True).count()
    high_risk = RiskAssessment.objects.filter(
        risk_level__in=['HIGH', 'CRITICAL']
    ).values('student').distinct().count()
    
    active_interventions = InterventionPlan.objects.filter(
        status__in=['APPROVED', 'IN_PROGRESS']
    ).count()
    
    return JsonResponse({
        'total_students': total_students,
        'high_risk_count': high_risk,
        'active_interventions': active_interventions,
        'timestamp': timezone.now().isoformat(),
    })


@login_required
def students_list(request):
    """View list of all students with filtering."""
    from django.core.paginator import Paginator
    
    # Get filters
    search = request.GET.get('search', '')
    school = request.GET.get('school', '')
    risk_level = request.GET.get('risk_level', '')
    grade = request.GET.get('grade', '')
    
    # Base queryset
    students = Student.objects.filter(is_active=True).select_related().prefetch_related('risk_assessments')
    
    # Apply filters
    if search:
        students = students.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(student_id__icontains=search)
        )
    
    if school:
        students = students.filter(school_name=school)
    
    if grade:
        students = students.filter(grade_level=grade)
    
    # Get latest risk assessment for each student
    students_with_risk = []
    for student in students:
        latest_risk = student.risk_assessments.order_by('-assessment_date').first()
        if risk_level and (not latest_risk or latest_risk.risk_level != risk_level):
            continue
        students_with_risk.append({
            'student': student,
            'risk': latest_risk
        })
    
    # Pagination
    paginator = Paginator(students_with_risk, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get unique schools and grades for filters
    schools = Student.objects.values_list('school_name', flat=True).distinct().order_by('school_name')
    grades = Student.objects.values_list('grade_level', flat=True).distinct().order_by('grade_level')
    
    context = {
        'page_obj': page_obj,
        'schools': schools,
        'grades': grades,
        'current_search': search,
        'current_school': school,
        'current_risk': risk_level,
        'current_grade': grade,
        'total_count': len(students_with_risk),
    }
    
    return render(request, 'dashboard/students_list.html', context)


@login_required
def student_detail(request, student_id):
    """View detailed information about a student."""
    from django.shortcuts import get_object_or_404
    from education.models import AttendanceRecord, GradeRecord, BehaviorNote
    
    student = get_object_or_404(Student, id=student_id)
    
    # Get all related data
    risk_assessments = student.risk_assessments.order_by('-assessment_date')[:5]
    interventions = student.intervention_plans.order_by('-created_at')[:5]
    
    # Get attendance records for display and statistics
    all_attendance = AttendanceRecord.objects.filter(student=student).order_by('-date')
    attendance = all_attendance[:30]
    
    # Get grades for display and statistics
    all_grades = GradeRecord.objects.filter(student=student).order_by('-exam_date')
    grades = all_grades[:20]
    
    behavior = BehaviorNote.objects.filter(student=student).order_by('-date')[:10]
    
    # Calculate statistics
    total_attendance = all_attendance.count()
    present_count = all_attendance.filter(status='PRESENT').count()
    attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0
    
    avg_grade = all_grades.aggregate(Avg('grade'))['grade__avg'] or 0
    
    context = {
        'student': student,
        'risk_assessments': risk_assessments,
        'interventions': interventions,
        'attendance_records': attendance,
        'grade_records': grades,
        'behavior_notes': behavior,
        'attendance_rate': round(attendance_rate, 1),
        'avg_grade': round(float(avg_grade), 2) if avg_grade else 0,
    }
    
    return render(request, 'dashboard/student_detail.html', context)


@login_required
def patients_list(request):
    """View list of all patients with filtering."""
    from django.core.paginator import Paginator
    from health.models import AdherenceRecord
    
    # Get filters
    search = request.GET.get('search', '')
    region = request.GET.get('region', '')
    risk_level = request.GET.get('risk_level', '')
    
    # Base queryset
    patients = Patient.objects.filter(is_active=True).select_related()
    
    # Apply filters
    if search:
        patients = patients.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(patient_id__icontains=search)
        )
    
    if region:
        patients = patients.filter(region=region)
    
    # Get latest adherence for each patient
    patients_with_adherence = []
    for patient in patients:
        latest_adherence = AdherenceRecord.objects.filter(patient=patient).order_by('-assessment_date').first()
        if risk_level and (not latest_adherence or latest_adherence.risk_level != risk_level):
            continue
        patients_with_adherence.append({
            'patient': patient,
            'adherence': latest_adherence
        })
    
    # Pagination
    paginator = Paginator(patients_with_adherence, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get unique regions for filters
    regions = Patient.objects.values_list('region', flat=True).distinct().order_by('region')
    
    context = {
        'page_obj': page_obj,
        'regions': regions,
        'current_search': search,
        'current_region': region,
        'current_risk': risk_level,
        'total_count': len(patients_with_adherence),
    }
    
    return render(request, 'dashboard/patients_list.html', context)


@login_required
def patient_detail(request, patient_id):
    """View detailed information about a patient."""
    from django.shortcuts import get_object_or_404
    from health.models import AdherenceRecord, FollowUpSession, ReferralAction
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get all related data
    adherence_records = AdherenceRecord.objects.filter(patient=patient).order_by('-assessment_date')[:5]
    
    # Get appointments for display and statistics
    all_appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    appointments = all_appointments[:20]
    
    follow_ups = FollowUpSession.objects.filter(patient=patient).order_by('-session_date')[:10]
    referrals = ReferralAction.objects.filter(patient=patient).order_by('-action_date')[:10]
    
    # Calculate statistics
    total_appointments = all_appointments.count()
    completed = all_appointments.filter(status='COMPLETED').count()
    missed = all_appointments.filter(status='MISSED').count()
    adherence_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
    
    # Get latest adherence
    latest_adherence = adherence_records.first()
    
    context = {
        'patient': patient,
        'adherence_records': adherence_records,
        'appointments': appointments,
        'follow_ups': follow_ups,
        'referrals': referrals,
        'total_appointments': total_appointments,
        'completed_appointments': completed,
        'missed_appointments': missed,
        'adherence_rate': round(adherence_rate, 1),
        'latest_adherence': latest_adherence,
    }
    
    return render(request, 'dashboard/patient_detail.html', context)


from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from accounts.permissions import IsSupervisor
from django.contrib.auth.decorators import user_passes_test
from education.models import RiskThreshold
from core.utils import create_audit_log


def is_supervisor(user):
    """Check if user has supervisor permission."""
    return user.is_authenticated and user.has_supervisor_permission


@login_required
@user_passes_test(is_supervisor)
def thresholds_list(request):
    """
    GET/POST /dashboard/thresholds/
    List all risk thresholds and handle creation.
    SUPERVISOR only.
    """
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            attendance_threshold = float(request.POST.get('attendance_threshold', 75.0))
            grade_threshold = float(request.POST.get('grade_threshold', 10.0))
            behavior_threshold = int(request.POST.get('behavior_threshold', 3))
            missed_appointments_threshold = int(request.POST.get('missed_appointments_threshold', 2))
            
            # Validate
            errors = []
            if not name:
                errors.append("Name is required")
            if not 0 <= attendance_threshold <= 100:
                errors.append("Attendance threshold must be between 0 and 100")
            if not 0 <= grade_threshold <= 20:
                errors.append("Grade threshold must be between 0 and 20")
            if behavior_threshold < 0:
                errors.append("Behavior threshold must be non-negative")
            if missed_appointments_threshold < 0:
                errors.append("Missed appointments threshold must be non-negative")
            
            if errors:
                for error in errors:
                    messages.error(request, error)
            else:
                # Create threshold
                threshold = RiskThreshold.objects.create(
                    name=name,
                    description=description,
                    attendance_threshold=attendance_threshold,
                    grade_threshold=grade_threshold,
                    behavior_threshold=behavior_threshold,
                    missed_appointments_threshold=missed_appointments_threshold,
                    is_active=False,
                    created_by=request.user
                )
                
                # Log the action
                create_audit_log(
                    user=request.user,
                    action_type='CREATE',
                    resource_type='RiskThreshold',
                    resource_id=threshold.id,
                    description=f'Created risk threshold: {name}',
                    result='SUCCESS',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, f'Risk threshold "{name}" created successfully')
                return redirect('dashboard:thresholds-list')
                
        except ValueError as e:
            messages.error(request, f'Invalid input: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error creating threshold: {str(e)}')
            create_audit_log(
                user=request.user,
                action_type='CREATE',
                resource_type='RiskThreshold',
                resource_id='0',
                description=f'Failed to create risk threshold: {str(e)}',
                result='FAILED',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
    
    # GET request - list all thresholds
    thresholds = RiskThreshold.objects.all()
    active_threshold = thresholds.filter(is_active=True).first()
    
    context = {
        'thresholds': thresholds,
        'active_threshold': active_threshold,
    }
    
    return render(request, 'dashboard/thresholds.html', context)


@login_required
@user_passes_test(is_supervisor)
def threshold_activate(request, threshold_id):
    """
    POST /dashboard/thresholds/<id>/activate/
    Activate a specific threshold.
    SUPERVISOR only.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method')
        return redirect('dashboard:thresholds-list')
    
    try:
        threshold = get_object_or_404(RiskThreshold, id=threshold_id)
        
        # Activate this threshold (will deactivate others automatically)
        threshold.is_active = True
        threshold.save()
        
        # Log the action
        create_audit_log(
            user=request.user,
            action_type='UPDATE',
            resource_type='RiskThreshold',
            resource_id=threshold.id,
            description=f'Activated risk threshold: {threshold.name}',
            result='SUCCESS',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, f'Risk threshold "{threshold.name}" activated successfully')
        
    except Exception as e:
        messages.error(request, f'Error activating threshold: {str(e)}')
        create_audit_log(
            user=request.user,
            action_type='UPDATE',
            resource_type='RiskThreshold',
            resource_id=threshold_id,
            description=f'Failed to activate risk threshold: {str(e)}',
            result='FAILED',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    return redirect('dashboard:thresholds-list')



# IMPROVEMENT 4: CSV/PDF Export Views

@login_required
@user_passes_test(is_supervisor)
def export_students_csv(request):
    """
    Export students data to CSV format.
    SUPERVISOR only.
    """
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Create HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Student ID', 'First Name', 'Last Name', 'Date of Birth', 'Gender',
        'School Name', 'Grade Level', 'Region', 'Guardian Name', 'Guardian Phone',
        'Enrollment Date', 'Is Active', 'Latest Risk Level', 'Latest Risk Score'
    ])
    
    # Get all students with their latest risk assessment
    students = Student.objects.filter(is_active=True).prefetch_related('risk_assessments')
    
    for student in students:
        latest_risk = student.risk_assessments.order_by('-assessment_date').first()
        
        writer.writerow([
            student.student_id,
            student.first_name,
            student.last_name,
            student.date_of_birth.strftime('%Y-%m-%d'),
            student.get_gender_display(),
            student.school_name,
            student.grade_level,
            student.region,
            student.guardian_name,
            student.guardian_phone,
            student.enrollment_date.strftime('%Y-%m-%d'),
            'Yes' if student.is_active else 'No',
            latest_risk.risk_level if latest_risk else 'N/A',
            f"{latest_risk.overall_risk_score:.2f}" if latest_risk else 'N/A'
        ])
    
    # Log the export
    create_audit_log(
        user=request.user,
        action_type='EXPORT',
        resource_type='Student',
        resource_id=str(students.count()),
        description=f'Exported {students.count()} students to CSV',
        result='SUCCESS',
        request=request
    )
    
    return response


@login_required
@user_passes_test(is_supervisor)
def export_patients_csv(request):
    """
    Export patients data to CSV format.
    SUPERVISOR only.
    """
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    from health.models import AdherenceRecord
    
    # Create HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="patients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Patient ID', 'First Name', 'Last Name', 'Date of Birth', 'Gender',
        'Region', 'Emergency Contact Name', 'Emergency Contact Phone', 'Registration Date',
        'Is Active', 'Latest Risk Level', 'Latest Adherence Rate'
    ])
    
    # Get all patients with their latest adherence
    patients = Patient.objects.filter(is_active=True)
    
    for patient in patients:
        latest_adherence = AdherenceRecord.objects.filter(patient=patient).order_by('-assessment_date').first()
        
        writer.writerow([
            patient.patient_id,
            patient.first_name,
            patient.last_name,
            patient.date_of_birth.strftime('%Y-%m-%d'),
            patient.get_gender_display(),
            patient.region,
            patient.emergency_contact_name,
            patient.emergency_contact_phone,
            patient.registration_date.strftime('%Y-%m-%d'),
            'Yes' if patient.is_active else 'No',
            latest_adherence.risk_level if latest_adherence else 'N/A',
            f"{latest_adherence.adherence_rate:.2f}" if latest_adherence else 'N/A'
        ])
    
    # Log the export
    create_audit_log(
        user=request.user,
        action_type='EXPORT',
        resource_type='Patient',
        resource_id=str(patients.count()),
        description=f'Exported {patients.count()} patients to CSV',
        result='SUCCESS',
        request=request
    )
    
    return response


@login_required
@user_passes_test(is_supervisor)
def export_report_pdf(request):
    """
    Export dashboard report to PDF format.
    SUPERVISOR only.
    Uses ReportLab for PDF generation with fallback to HTML.
    """
    from django.http import HttpResponse
    from datetime import datetime, timedelta
    
    try:
        # Try to use ReportLab if available
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        # Create HTTP response with PDF content type
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="dashboard_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3498db'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("Youth Support Platform", title_style))
        story.append(Paragraph("Dashboard Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Get data
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        
        # KPIs
        total_students = Student.objects.filter(is_active=True).count()
        recent_assessments = RiskAssessment.objects.filter(assessment_date__gte=thirty_days_ago)
        high_risk_count = recent_assessments.filter(risk_level__in=['HIGH', 'CRITICAL']).values('student').distinct().count()
        active_interventions = InterventionPlan.objects.filter(status__in=['APPROVED', 'IN_PROGRESS']).count()
        
        # KPIs Section
        story.append(Paragraph("Key Performance Indicators", heading_style))
        
        kpi_data = [
            ['Metric', 'Value'],
            ['Total Active Students', str(total_students)],
            ['High Risk Students', str(high_risk_count)],
            ['Active Interventions', str(active_interventions)],
            ['Assessment Period', 'Last 30 Days']
        ]
        
        kpi_table = Table(kpi_data, colWidths=[3.5*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(kpi_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Distribution
        story.append(Paragraph("Risk Level Distribution", heading_style))
        
        risk_data = [
            ['Risk Level', 'Count'],
            ['Low', str(recent_assessments.filter(risk_level='LOW').count())],
            ['Medium', str(recent_assessments.filter(risk_level='MEDIUM').count())],
            ['High', str(recent_assessments.filter(risk_level='HIGH').count())],
            ['Critical', str(recent_assessments.filter(risk_level='CRITICAL').count())]
        ]
        
        risk_table = Table(risk_data, colWidths=[3.5*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(risk_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Critical Alerts
        story.append(Paragraph("Critical Alerts (Top 5)", heading_style))
        
        critical_alerts = RiskAssessment.objects.filter(
            risk_level='CRITICAL',
            assessment_date__gte=thirty_days_ago
        ).select_related('student').order_by('-assessment_date')[:5]
        
        if critical_alerts:
            alert_data = [['Student', 'School', 'Risk Score', 'Date']]
            for alert in critical_alerts:
                alert_data.append([
                    alert.student.full_name,
                    alert.student.school_name[:30],
                    f"{alert.overall_risk_score:.1f}",
                    alert.assessment_date.strftime('%Y-%m-%d')
                ])
            
            alert_table = Table(alert_data, colWidths=[2*inch, 2*inch, 1*inch, 1.5*inch])
            alert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(alert_table)
        else:
            story.append(Paragraph("No critical alerts in the last 30 days.", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Youth Support Platform - SESAME University", styles['Normal']))
        story.append(Paragraph("This report contains synthetic data for educational purposes only.", styles['Italic']))
        
        # Build PDF
        doc.build(story)
        
        # Log the export
        create_audit_log(
            user=request.user,
            action_type='EXPORT',
            resource_type='Report',
            resource_id='PDF',
            description='Exported dashboard report to PDF',
            result='SUCCESS',
            request=request
        )
        
        return response
        
    except ImportError:
        # Fallback: Return HTML version if ReportLab not available
        messages.warning(request, 'PDF export requires ReportLab library. Showing HTML version instead.')
        return redirect('dashboard:reports')



# IMPROVEMENT 5: Health Check Endpoint

from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
import sys


def health_check(request):
    """
    System health check endpoint for monitoring.
    Returns JSON with system status, database connectivity, and metrics.
    Public endpoint (no authentication required).
    """
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {}
    }
    
    # 1. Database connectivity check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
    
    # 2. Data integrity check
    try:
        student_count = Student.objects.count()
        patient_count = Patient.objects.count()
        assessment_count = RiskAssessment.objects.count()
        
        health_status['checks']['data_integrity'] = {
            'status': 'healthy',
            'metrics': {
                'students': student_count,
                'patients': patient_count,
                'risk_assessments': assessment_count
            }
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['data_integrity'] = {
            'status': 'unhealthy',
            'message': f'Data integrity check failed: {str(e)}'
        }
    
    # 3. System resources check
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status['checks']['system_resources'] = {
            'status': 'healthy' if cpu_percent < 90 and memory.percent < 90 else 'warning',
            'metrics': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent
            }
        }
    except ImportError:
        # psutil not installed, skip this check
        health_status['checks']['system_resources'] = {
            'status': 'skipped',
            'message': 'psutil not installed, resource monitoring unavailable'
        }
    except Exception as e:
        health_status['checks']['system_resources'] = {
            'status': 'warning',
            'message': f'Resource check failed: {str(e)}'
        }
    
    # 4. Python version check
    health_status['checks']['python_version'] = {
        'status': 'healthy',
        'version': sys.version,
        'version_info': {
            'major': sys.version_info.major,
            'minor': sys.version_info.minor,
            'micro': sys.version_info.micro
        }
    }
    
    # 5. Django settings check
    from django.conf import settings
    health_status['checks']['django_settings'] = {
        'status': 'healthy',
        'debug_mode': settings.DEBUG,
        'database_engine': settings.DATABASES['default']['ENGINE']
    }
    
    # 6. Recent activity check (last 24 hours)
    try:
        from datetime import timedelta
        yesterday = timezone.now() - timedelta(days=1)
        recent_logs = AuditLog.objects.filter(timestamp__gte=yesterday).count()
        recent_assessments = RiskAssessment.objects.filter(assessment_date__gte=yesterday.date()).count()
        
        health_status['checks']['recent_activity'] = {
            'status': 'healthy',
            'metrics': {
                'audit_logs_24h': recent_logs,
                'risk_assessments_24h': recent_assessments
            }
        }
    except Exception as e:
        health_status['checks']['recent_activity'] = {
            'status': 'warning',
            'message': f'Activity check failed: {str(e)}'
        }
    
    # Determine overall status
    unhealthy_checks = [k for k, v in health_status['checks'].items() if v.get('status') == 'unhealthy']
    warning_checks = [k for k, v in health_status['checks'].items() if v.get('status') == 'warning']
    
    if unhealthy_checks:
        health_status['status'] = 'unhealthy'
        health_status['unhealthy_checks'] = unhealthy_checks
    elif warning_checks:
        health_status['status'] = 'warning'
        health_status['warning_checks'] = warning_checks
    
    # Set HTTP status code based on health
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)

