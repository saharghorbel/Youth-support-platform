"""
Serializers for education app.
"""
from rest_framework import serializers
from .models import (
    Student, AttendanceRecord, GradeRecord,
    BehaviorNote, RiskAssessment, InterventionPlan
)


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model."""
    
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'gender', 'school_name', 'grade_level',
            'region', 'guardian_name', 'guardian_phone', 'guardian_email',
            'enrollment_date', 'is_active', 'notes',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def validate_student_id(self, value):
        """Ensure student_id is unique."""
        if self.instance and self.instance.student_id == value:
            return value
        if Student.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("Student ID already exists.")
        return value


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceRecord model."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'student', 'student_name', 'date', 'status', 'reason',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def validate(self, data):
        """Ensure no duplicate attendance for same student and date."""
        student = data.get('student')
        date = data.get('date')
        
        if self.instance:
            # Update case - exclude current instance
            if AttendanceRecord.objects.filter(
                student=student, date=date
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    "Attendance record already exists for this student and date."
                )
        else:
            # Create case
            if AttendanceRecord.objects.filter(student=student, date=date).exists():
                raise serializers.ValidationError(
                    "Attendance record already exists for this student and date."
                )
        
        return data


class GradeRecordSerializer(serializers.ModelSerializer):
    """Serializer for GradeRecord model."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = GradeRecord
        fields = [
            'id', 'student', 'student_name', 'subject', 'grade',
            'exam_date', 'exam_type', 'comments',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def validate_grade(self, value):
        """Ensure grade is between 0 and 20."""
        if value < 0 or value > 20:
            raise serializers.ValidationError("Grade must be between 0 and 20.")
        return value


class BehaviorNoteSerializer(serializers.ModelSerializer):
    """Serializer for BehaviorNote model."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = BehaviorNote
        fields = [
            'id', 'student', 'student_name', 'date', 'severity',
            'category', 'description', 'action_taken',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class RiskAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for RiskAssessment model."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    
    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'student', 'student_name', 'student_id', 'assessment_date',
            'attendance_score', 'academic_score', 'behavior_score',
            'overall_risk_score', 'risk_level', 'explanation', 'recommendations',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'assessment_date', 'created_at', 'updated_at', 'created_by', 'updated_by']


class InterventionPlanSerializer(serializers.ModelSerializer):
    """Serializer for InterventionPlan model."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    risk_level = serializers.CharField(source='risk_assessment.risk_level', read_only=True)
    
    class Meta:
        model = InterventionPlan
        fields = [
            'id', 'student', 'student_name', 'risk_assessment', 'risk_level',
            'title', 'description', 'status', 'start_date', 'target_end_date',
            'actual_end_date', 'assigned_to', 'assigned_to_name',
            'goals', 'actions', 'progress_notes', 'outcome',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def validate(self, data):
        """Validate dates."""
        start_date = data.get('start_date')
        target_end_date = data.get('target_end_date')
        
        if start_date and target_end_date and start_date > target_end_date:
            raise serializers.ValidationError(
                "Start date must be before target end date."
            )
        
        return data


class StudentDetailSerializer(StudentSerializer):
    """Detailed student serializer with related data."""
    
    recent_attendance = AttendanceRecordSerializer(
        source='attendance_records',
        many=True,
        read_only=True
    )
    recent_grades = GradeRecordSerializer(
        source='grade_records',
        many=True,
        read_only=True
    )
    latest_risk_assessment = RiskAssessmentSerializer(read_only=True)
    active_interventions = InterventionPlanSerializer(
        many=True,
        read_only=True
    )
    
    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + [
            'recent_attendance', 'recent_grades',
            'latest_risk_assessment', 'active_interventions'
        ]
