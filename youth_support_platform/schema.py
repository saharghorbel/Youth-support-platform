"""
GraphQL schema for Youth Support Platform.
"""
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from accounts.models import User, AuditLog
from education.models import (
    Student, AttendanceRecord, GradeRecord,
    BehaviorNote, RiskAssessment, InterventionPlan
)
from health.models import (
    Patient, Appointment, FollowUpSession,
    AdherenceRecord, ReferralAction
)


# Accounts Types
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'organization', 'phone_number', 'is_active',
            'created_at', 'updated_at'
        )


class AuditLogType(DjangoObjectType):
    class Meta:
        model = AuditLog
        fields = (
            'id', 'user', 'action_type', 'resource_type', 'resource_id',
            'description', 'result', 'reason', 'timestamp'
        )


# Education Types
class StudentType(DjangoObjectType):
    full_name = graphene.String()
    age = graphene.Int()
    
    class Meta:
        model = Student
        fields = (
            'id', 'student_id', 'first_name', 'last_name',
            'date_of_birth', 'gender', 'school_name', 'grade_level',
            'region', 'guardian_name', 'guardian_phone',
            'enrollment_date', 'is_active', 'created_at'
        )
    
    def resolve_full_name(self, info):
        return self.full_name
    
    def resolve_age(self, info):
        return self.age


class AttendanceRecordType(DjangoObjectType):
    class Meta:
        model = AttendanceRecord
        fields = (
            'id', 'student', 'date', 'status', 'reason', 'created_at'
        )


class GradeRecordType(DjangoObjectType):
    class Meta:
        model = GradeRecord
        fields = (
            'id', 'student', 'subject', 'grade', 'exam_date',
            'exam_type', 'comments', 'created_at'
        )


class BehaviorNoteType(DjangoObjectType):
    class Meta:
        model = BehaviorNote
        fields = (
            'id', 'student', 'date', 'severity', 'category',
            'description', 'action_taken', 'created_at'
        )


class RiskAssessmentType(DjangoObjectType):
    class Meta:
        model = RiskAssessment
        fields = (
            'id', 'student', 'assessment_date', 'attendance_score',
            'academic_score', 'behavior_score', 'overall_risk_score',
            'risk_level', 'explanation', 'recommendations'
        )


class InterventionPlanType(DjangoObjectType):
    class Meta:
        model = InterventionPlan
        fields = (
            'id', 'student', 'risk_assessment', 'title', 'description',
            'status', 'start_date', 'target_end_date', 'assigned_to',
            'goals', 'actions', 'created_at'
        )


# Health Types
class PatientType(DjangoObjectType):
    full_name = graphene.String()
    
    class Meta:
        model = Patient
        fields = (
            'id', 'patient_id', 'first_name', 'last_name',
            'date_of_birth', 'gender', 'phone_number', 'region',
            'registration_date', 'is_active', 'created_at'
        )
    
    def resolve_full_name(self, info):
        return self.full_name


class AppointmentType(DjangoObjectType):
    class Meta:
        model = Appointment
        fields = (
            'id', 'patient', 'appointment_date', 'appointment_time',
            'appointment_type', 'status', 'provider_name', 'location',
            'reason', 'created_at'
        )


class FollowUpSessionType(DjangoObjectType):
    class Meta:
        model = FollowUpSession
        fields = (
            'id', 'patient', 'appointment', 'session_date',
            'session_duration', 'provider_name', 'mood_score',
            'anxiety_score', 'treatment_plan', 'created_at'
        )


class AdherenceRecordType(DjangoObjectType):
    class Meta:
        model = AdherenceRecord
        fields = (
            'id', 'patient', 'assessment_date', 'total_appointments',
            'attended_appointments', 'missed_appointments',
            'adherence_rate', 'consecutive_missed', 'risk_level'
        )


class ReferralActionType(DjangoObjectType):
    class Meta:
        model = ReferralAction
        fields = (
            'id', 'patient', 'action_type', 'status', 'trigger_reason',
            'action_date', 'completed_date', 'assigned_to', 'outcome'
        )


# Queries
class Query(graphene.ObjectType):
    # User queries
    me = graphene.Field(UserType)
    all_users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int())
    
    # Education queries
    all_students = graphene.List(StudentType, school_name=graphene.String(), region=graphene.String())
    student = graphene.Field(StudentType, id=graphene.Int())
    student_by_id = graphene.Field(StudentType, student_id=graphene.String())
    
    all_risk_assessments = graphene.List(RiskAssessmentType, risk_level=graphene.String())
    risk_assessment = graphene.Field(RiskAssessmentType, id=graphene.Int())
    student_risk_assessments = graphene.List(RiskAssessmentType, student_id=graphene.Int())
    
    all_interventions = graphene.List(InterventionPlanType, status=graphene.String())
    intervention = graphene.Field(InterventionPlanType, id=graphene.Int())
    
    # Health queries
    all_patients = graphene.List(PatientType, region=graphene.String())
    patient = graphene.Field(PatientType, id=graphene.Int())
    patient_by_id = graphene.Field(PatientType, patient_id=graphene.String())
    
    all_appointments = graphene.List(AppointmentType, status=graphene.String())
    appointment = graphene.Field(AppointmentType, id=graphene.Int())
    patient_appointments = graphene.List(AppointmentType, patient_id=graphene.Int())
    
    all_adherence_records = graphene.List(AdherenceRecordType, risk_level=graphene.String())
    patient_adherence = graphene.Field(AdherenceRecordType, patient_id=graphene.Int())
    
    # Audit logs
    all_audit_logs = graphene.List(AuditLogType, action_type=graphene.String())
    
    # User resolvers
    def resolve_me(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return user
    
    def resolve_all_users(self, info):
        user = info.context.user
        if not user.is_authenticated or not user.has_admin_permission():
            raise GraphQLError('Permission denied')
        return User.objects.all()
    
    def resolve_user(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return User.objects.get(pk=id)
    
    # Education resolvers
    def resolve_all_students(self, info, school_name=None, region=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        
        queryset = Student.objects.all()
        if school_name:
            queryset = queryset.filter(school_name__icontains=school_name)
        if region:
            queryset = queryset.filter(region=region)
        return queryset
    
    def resolve_student(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return Student.objects.get(pk=id)
    
    def resolve_student_by_id(self, info, student_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return Student.objects.get(student_id=student_id)
    
    def resolve_all_risk_assessments(self, info, risk_level=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        
        queryset = RiskAssessment.objects.all()
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        return queryset
    
    def resolve_risk_assessment(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return RiskAssessment.objects.get(pk=id)
    
    def resolve_student_risk_assessments(self, info, student_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return RiskAssessment.objects.filter(student_id=student_id)
    
    def resolve_all_interventions(self, info, status=None):
        user = info.context.user
        if not user.is_authenticated or not user.has_supervisor_permission():
            raise GraphQLError('Permission denied')
        
        queryset = InterventionPlan.objects.all()
        if status:
            queryset = queryset.filter(status=status)
        return queryset
    
    def resolve_intervention(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return InterventionPlan.objects.get(pk=id)
    
    # Health resolvers
    def resolve_all_patients(self, info, region=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        
        queryset = Patient.objects.all()
        if region:
            queryset = queryset.filter(region=region)
        return queryset
    
    def resolve_patient(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return Patient.objects.get(pk=id)
    
    def resolve_patient_by_id(self, info, patient_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return Patient.objects.get(patient_id=patient_id)
    
    def resolve_all_appointments(self, info, status=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        
        queryset = Appointment.objects.all()
        if status:
            queryset = queryset.filter(status=status)
        return queryset
    
    def resolve_appointment(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return Appointment.objects.get(pk=id)
    
    def resolve_patient_appointments(self, info, patient_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return Appointment.objects.filter(patient_id=patient_id)
    
    def resolve_all_adherence_records(self, info, risk_level=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        
        queryset = AdherenceRecord.objects.all()
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        return queryset
    
    def resolve_patient_adherence(self, info, patient_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Not authenticated')
        return AdherenceRecord.objects.filter(patient_id=patient_id).order_by('-assessment_date').first()
    
    def resolve_all_audit_logs(self, info, action_type=None):
        user = info.context.user
        if not user.is_authenticated or not user.has_admin_permission():
            raise GraphQLError('Permission denied')
        
        queryset = AuditLog.objects.all()
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        return queryset


# Mutations
class CreateStudent(graphene.Mutation):
    class Arguments:
        student_id = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        date_of_birth = graphene.Date(required=True)
        gender = graphene.String(required=True)
        school_name = graphene.String(required=True)
        grade_level = graphene.Int(required=True)
        region = graphene.String(required=True)
        guardian_name = graphene.String(required=True)
        guardian_phone = graphene.String(required=True)
        enrollment_date = graphene.Date(required=True)
    
    student = graphene.Field(StudentType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated or not user.has_operator_permission():
            return CreateStudent(success=False, message='Permission denied')
        
        try:
            student = Student.objects.create(
                created_by=user,
                **kwargs
            )
            return CreateStudent(student=student, success=True, message='Student created successfully')
        except Exception as e:
            return CreateStudent(success=False, message=str(e))


class CreatePatient(graphene.Mutation):
    class Arguments:
        patient_id = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        date_of_birth = graphene.Date(required=True)
        gender = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        region = graphene.String(required=True)
        emergency_contact_name = graphene.String(required=True)
        emergency_contact_phone = graphene.String(required=True)
        registration_date = graphene.Date(required=True)
    
    patient = graphene.Field(PatientType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated or not user.has_operator_permission():
            return CreatePatient(success=False, message='Permission denied')
        
        try:
            patient = Patient.objects.create(
                created_by=user,
                **kwargs
            )
            return CreatePatient(patient=patient, success=True, message='Patient created successfully')
        except Exception as e:
            return CreatePatient(success=False, message=str(e))


class Mutation(graphene.ObjectType):
    create_student = CreateStudent.Field()
    create_patient = CreatePatient.Field()


# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)
