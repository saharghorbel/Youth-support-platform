"""
Views for education app - Scenario 1: Education Early Warning System.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from .models import (
    Student, AttendanceRecord, GradeRecord,
    BehaviorNote, RiskAssessment, InterventionPlan
)
from .serializers import (
    StudentSerializer, StudentDetailSerializer,
    AttendanceRecordSerializer, GradeRecordSerializer,
    BehaviorNoteSerializer, RiskAssessmentSerializer,
    InterventionPlanSerializer
)
from accounts.permissions import IsOperator, IsSupervisor
from core.utils import create_audit_log


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student management.
    Operators can create/update, Supervisors can view all.
    """
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated, IsOperator]
    filterset_fields = ['school_name', 'grade_level', 'region', 'is_active']
    search_fields = ['first_name', 'last_name', 'student_id']
    ordering_fields = ['last_name', 'created_at', 'grade_level']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentSerializer
    
    def perform_create(self, serializer):
        """Set created_by field."""
        student = serializer.save(created_by=self.request.user)
        
        create_audit_log(
            user=self.request.user,
            action_type='CREATE',
            resource_type='Student',
            resource_id=str(student.id),
            description=f"Created student {student.full_name}",
            result='SUCCESS',
            request=self.request
        )
    
    def perform_update(self, serializer):
        """Set updated_by field."""
        student = serializer.save(updated_by=self.request.user)
        
        create_audit_log(
            user=self.request.user,
            action_type='UPDATE',
            resource_type='Student',
            resource_id=str(student.id),
            description=f"Updated student {student.full_name}",
            result='SUCCESS',
            request=self.request
        )
    
    @action(detail=True, methods=['get'])
    def risk_assessment(self, request, pk=None):
        """Get latest risk assessment for student."""
        student = self.get_object()
        assessment = student.risk_assessments.order_by('-assessment_date').first()
        
        if not assessment:
            return Response(
                {'detail': 'No risk assessment found for this student.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RiskAssessmentSerializer(assessment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def calculate_risk(self, request, pk=None):
        """Calculate and create new risk assessment for student."""
        student = self.get_object()
        
        # Calculate attendance score (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        attendance_records = student.attendance_records.filter(date__gte=thirty_days_ago)
        
        if attendance_records.exists():
            present_count = attendance_records.filter(status='PRESENT').count()
            total_count = attendance_records.count()
            attendance_score = (present_count / total_count) * 100
        else:
            attendance_score = 100  # No data = assume good
        
        # Calculate academic score (last 3 months)
        three_months_ago = date.today() - timedelta(days=90)
        grade_records = student.grade_records.filter(exam_date__gte=three_months_ago)
        
        if grade_records.exists():
            avg_grade = grade_records.aggregate(Avg('grade'))['grade__avg']
            academic_score = (avg_grade / 20) * 100  # Convert to percentage
        else:
            academic_score = 100  # No data = assume good
        
        # Calculate behavior score (last 30 days)
        behavior_notes = student.behavior_notes.filter(date__gte=thirty_days_ago)
        
        if behavior_notes.exists():
            severity_weights = {
                'POSITIVE': 20,
                'NEUTRAL': 0,
                'MINOR': -10,
                'MODERATE': -20,
                'SERIOUS': -40
            }
            
            total_weight = sum(
                severity_weights.get(note.severity, 0)
                for note in behavior_notes
            )
            
            # Base score 100, adjust by weighted notes
            behavior_score = max(0, min(100, 100 + (total_weight / behavior_notes.count())))
        else:
            behavior_score = 100  # No data = assume good
        
        # Calculate overall risk score (weighted average)
        overall_risk_score = (
            (attendance_score * 0.4) +
            (academic_score * 0.4) +
            (behavior_score * 0.2)
        )
        
        # Determine risk level
        if overall_risk_score >= 80:
            risk_level = 'LOW'
        elif overall_risk_score >= 60:
            risk_level = 'MEDIUM'
        elif overall_risk_score >= 40:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'
        
        # Generate explanation
        factors = []
        if attendance_score < 80:
            factors.append(f"Low attendance ({attendance_score:.1f}%)")
        if academic_score < 60:
            factors.append(f"Poor academic performance ({academic_score:.1f}%)")
        if behavior_score < 70:
            factors.append(f"Behavioral concerns ({behavior_score:.1f}%)")
        
        explanation = (
            f"Risk assessment based on: "
            f"Attendance ({attendance_score:.1f}%), "
            f"Academic performance ({academic_score:.1f}%), "
            f"Behavior ({behavior_score:.1f}%). "
        )
        
        if factors:
            explanation += "Key concerns: " + ", ".join(factors) + "."
        else:
            explanation += "Student is performing well across all indicators."
        
        # Generate recommendations
        recommendations = []
        if attendance_score < 80:
            recommendations.append("- Contact guardian about attendance issues")
            recommendations.append("- Investigate barriers to attendance")
        if academic_score < 60:
            recommendations.append("- Provide academic tutoring support")
            recommendations.append("- Review learning difficulties")
        if behavior_score < 70:
            recommendations.append("- Counseling sessions recommended")
            recommendations.append("- Behavioral intervention plan needed")
        
        if not recommendations:
            recommendations.append("- Continue monitoring student progress")
            recommendations.append("- Maintain current support level")
        
        recommendations_text = "\n".join(recommendations)
        
        # Create risk assessment
        assessment = RiskAssessment.objects.create(
            student=student,
            attendance_score=Decimal(str(round(attendance_score, 2))),
            academic_score=Decimal(str(round(academic_score, 2))),
            behavior_score=Decimal(str(round(behavior_score, 2))),
            overall_risk_score=Decimal(str(round(overall_risk_score, 2))),
            risk_level=risk_level,
            explanation=explanation,
            recommendations=recommendations_text,
            created_by=request.user
        )
        
        create_audit_log(
            user=request.user,
            action_type='CREATE',
            resource_type='RiskAssessment',
            resource_id=str(assessment.id),
            description=f"Calculated risk assessment for {student.full_name}: {risk_level}",
            result='SUCCESS',
            request=request
        )
        
        serializer = RiskAssessmentSerializer(assessment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for AttendanceRecord management."""
    
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, IsOperator]
    filterset_fields = ['student', 'date', 'status']
    ordering_fields = ['date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class GradeRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for GradeRecord management."""
    
    queryset = GradeRecord.objects.all()
    serializer_class = GradeRecordSerializer
    permission_classes = [IsAuthenticated, IsOperator]
    filterset_fields = ['student', 'subject', 'exam_type']
    ordering_fields = ['exam_date', 'grade']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class BehaviorNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for BehaviorNote management."""
    
    queryset = BehaviorNote.objects.all()
    serializer_class = BehaviorNoteSerializer
    permission_classes = [IsAuthenticated, IsOperator]
    filterset_fields = ['student', 'severity', 'category']
    ordering_fields = ['date', 'severity']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class RiskAssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing RiskAssessment (read-only, created via calculate_risk)."""
    
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'risk_level']
    ordering_fields = ['assessment_date', 'overall_risk_score']


class InterventionPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InterventionPlan management.
    Supervisors can create and approve plans.
    """
    queryset = InterventionPlan.objects.all()
    serializer_class = InterventionPlanSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]
    filterset_fields = ['student', 'status', 'assigned_to']
    ordering_fields = ['created_at', 'start_date']
    
    def perform_create(self, serializer):
        """Set created_by field."""
        plan = serializer.save(created_by=self.request.user)
        
        create_audit_log(
            user=self.request.user,
            action_type='CREATE',
            resource_type='InterventionPlan',
            resource_id=str(plan.id),
            description=f"Created intervention plan '{plan.title}' for {plan.student.full_name}",
            result='SUCCESS',
            request=self.request
        )
    
    def perform_update(self, serializer):
        """Set updated_by field."""
        plan = serializer.save(updated_by=self.request.user)
        
        create_audit_log(
            user=self.request.user,
            action_type='UPDATE',
            resource_type='InterventionPlan',
            resource_id=str(plan.id),
            description=f"Updated intervention plan '{plan.title}'",
            result='SUCCESS',
            request=self.request
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an intervention plan (Supervisor only)."""
        plan = self.get_object()
        
        if plan.status != 'PENDING':
            return Response(
                {'detail': 'Only pending plans can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = 'APPROVED'
        plan.updated_by = request.user
        plan.save()
        
        create_audit_log(
            user=request.user,
            action_type='APPROVE',
            resource_type='InterventionPlan',
            resource_id=str(plan.id),
            description=f"Approved intervention plan '{plan.title}'",
            result='SUCCESS',
            request=request
        )
        
        serializer = self.get_serializer(plan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an intervention plan (Supervisor only)."""
        plan = self.get_object()
        reason = request.data.get('reason', '')
        
        if plan.status != 'PENDING':
            return Response(
                {'detail': 'Only pending plans can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = 'CANCELLED'
        plan.progress_notes = f"Rejected: {reason}"
        plan.updated_by = request.user
        plan.save()
        
        create_audit_log(
            user=request.user,
            action_type='REJECT',
            resource_type='InterventionPlan',
            resource_id=str(plan.id),
            description=f"Rejected intervention plan '{plan.title}': {reason}",
            result='SUCCESS',
            request=request
        )
        
        serializer = self.get_serializer(plan)
        return Response(serializer.data)
