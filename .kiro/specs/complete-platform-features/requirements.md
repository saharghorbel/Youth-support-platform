# Requirements Document

## Introduction

This document specifies the requirements for completing the Youth Support Platform, a Django-based system for Tunisian social services (education and health sectors). The platform currently has a foundational structure with 6 Django apps, 13 data models, custom user authentication with 3 roles, basic dashboard views, and database migrations. This specification covers the implementation of complete REST and GraphQL APIs, enhanced dashboard UI, AI/ML risk prediction models, comprehensive testing, and complete documentation to make the platform exam-ready and production-capable.

## Glossary

- **System**: The Youth Support Platform Django application
- **REST_API**: RESTful API endpoints using Django REST Framework
- **GraphQL_API**: GraphQL endpoint using Graphene-Django
- **Dashboard**: Web-based monitoring and reporting interface
- **AI_Engine**: Machine learning components for risk prediction
- **Test_Suite**: Comprehensive automated testing framework
- **Operator**: User role that creates and updates records
- **Supervisor**: User role that validates records and plans interventions
- **Admin**: User role that configures policies and monitors outcomes
- **Student**: Education sector entity tracked for disengagement risk
- **Patient**: Health sector entity tracked for adherence and appointments
- **Risk_Assessment**: Calculated evaluation of student disengagement risk
- **Adherence_Record**: Calculated evaluation of patient treatment adherence
- **Intervention_Plan**: Action plan for at-risk students
- **Referral_Action**: Follow-up action for patients with low adherence
- **ViewSet**: Django REST Framework class for CRUD operations
- **Serializer**: Django REST Framework class for data validation and transformation
- **GraphQL_Schema**: Type definitions and resolvers for GraphQL API
- **Permission_Class**: Django REST Framework class for access control
- **Test_Fixture**: Predefined test data for automated testing
- **Property_Based_Test**: Test that verifies properties hold for generated inputs
- **ML_Model**: Trained machine learning model for predictions
- **KPI**: Key Performance Indicator displayed on dashboard
- **API_Documentation**: OpenAPI/Swagger specification for REST endpoints


## Requirements

### Requirement 1: Complete Education REST API

**User Story:** As an Operator, I want to manage education records through REST API endpoints, so that I can create and update student data programmatically.

#### Acceptance Criteria

1. THE REST_API SHALL provide ViewSets for Student, AttendanceRecord, GradeRecord, BehaviorNote, RiskAssessment, and InterventionPlan models
2. WHEN an authenticated user requests student data, THE REST_API SHALL return paginated results with 20 items per page
3. THE REST_API SHALL support filtering by school_name, grade_level, region, and risk_level
4. THE REST_API SHALL support searching by student_id, first_name, and last_name
5. THE REST_API SHALL support ordering by created_at, assessment_date, and risk_level
6. WHEN an Operator creates a student record, THE REST_API SHALL validate all required fields and return validation errors for invalid data
7. WHEN a Supervisor requests intervention plans, THE REST_API SHALL filter results to show only plans assigned to them or unassigned plans
8. THE REST_API SHALL enforce role-based permissions where Operators can create and update, Supervisors can approve, and Admins can delete

### Requirement 2: Complete Health REST API

**User Story:** As an Operator, I want to manage health records through REST API endpoints, so that I can track patient appointments and adherence programmatically.

#### Acceptance Criteria

1. THE REST_API SHALL provide ViewSets for Patient, Appointment, FollowUpSession, AdherenceRecord, and ReferralAction models
2. WHEN an authenticated user requests patient data, THE REST_API SHALL return paginated results with 20 items per page
3. THE REST_API SHALL support filtering by region, appointment_status, adherence_risk_level, and action_type
4. THE REST_API SHALL support searching by patient_id, first_name, and last_name
5. THE REST_API SHALL support ordering by appointment_date, session_date, and assessment_date
6. WHEN an Operator creates an appointment, THE REST_API SHALL validate date is not in the past and return validation errors for invalid data
7. WHEN a missed appointment is recorded, THE REST_API SHALL automatically create a pending ReferralAction
8. THE REST_API SHALL enforce role-based permissions where Operators can create and update, Supervisors can assign referrals, and Admins can view all records

### Requirement 3: REST API Serialization and Validation

**User Story:** As a developer, I want robust data serialization and validation, so that API consumers receive consistent, validated data.

#### Acceptance Criteria

1. THE Serializer SHALL validate student_id and patient_id are unique before creation
2. THE Serializer SHALL validate date_of_birth is not in the future
3. THE Serializer SHALL validate grade values are between 0 and 20
4. THE Serializer SHALL validate phone numbers match the pattern for Tunisian phone numbers
5. THE Serializer SHALL validate email addresses are properly formatted
6. WHEN validation fails, THE Serializer SHALL return structured error messages with field names and error descriptions
7. THE Serializer SHALL include nested related data for detail views (student with recent attendance, grades, and risk assessments)
8. THE Serializer SHALL exclude sensitive fields (medical_notes, guardian_email) from list views unless user has Supervisor or Admin role


### Requirement 4: Complete GraphQL Schema

**User Story:** As a frontend developer, I want a complete GraphQL API, so that I can query exactly the data I need in a single request.

#### Acceptance Criteria

1. THE GraphQL_Schema SHALL define types for all 13 models (User, Student, AttendanceRecord, GradeRecord, BehaviorNote, RiskAssessment, InterventionPlan, Patient, Appointment, FollowUpSession, AdherenceRecord, ReferralAction, AuditLog)
2. THE GraphQL_Schema SHALL provide queries for listing and retrieving individual records of each type
3. THE GraphQL_Schema SHALL support filtering arguments (region, risk_level, status, date_range)
4. THE GraphQL_Schema SHALL support pagination with first, last, before, and after arguments
5. THE GraphQL_Schema SHALL provide mutations for creating Student, Patient, Appointment, AttendanceRecord, GradeRecord, and InterventionPlan
6. THE GraphQL_Schema SHALL provide mutations for updating status fields (appointment_status, intervention_status, referral_status)
7. WHEN a GraphQL query requests nested data, THE GraphQL_Schema SHALL resolve relationships efficiently using DataLoader to prevent N+1 queries
8. THE GraphQL_Schema SHALL enforce authentication where unauthenticated requests return an error

### Requirement 5: GraphQL Authorization

**User Story:** As a system administrator, I want GraphQL queries to respect role-based permissions, so that users can only access data appropriate to their role.

#### Acceptance Criteria

1. WHEN an Operator queries intervention plans, THE GraphQL_Schema SHALL return only plans in DRAFT or PENDING status
2. WHEN a Supervisor queries intervention plans, THE GraphQL_Schema SHALL return all plans except CANCELLED
3. WHEN an Admin queries intervention plans, THE GraphQL_Schema SHALL return all plans regardless of status
4. THE GraphQL_Schema SHALL prevent Operators from executing mutations that change status to APPROVED or COMPLETED
5. THE GraphQL_Schema SHALL prevent non-Admins from querying AuditLog records
6. WHEN an unauthorized mutation is attempted, THE GraphQL_Schema SHALL return an error with message "Insufficient permissions"
7. THE GraphQL_Schema SHALL log all mutation attempts to AuditLog with user, action, and result
8. THE GraphQL_Schema SHALL validate user role before executing any mutation

### Requirement 6: Enhanced Dashboard KPIs

**User Story:** As a Supervisor, I want real-time KPI updates on the dashboard, so that I can monitor system performance without page refresh.

#### Acceptance Criteria

1. THE Dashboard SHALL display total active students count
2. THE Dashboard SHALL display count of students with HIGH or CRITICAL risk level from last 30 days
3. THE Dashboard SHALL display count of active intervention plans (APPROVED or IN_PROGRESS status)
4. THE Dashboard SHALL display intervention completion rate as percentage
5. THE Dashboard SHALL display risk distribution chart showing counts for LOW, MEDIUM, HIGH, and CRITICAL levels
6. THE Dashboard SHALL provide an AJAX endpoint that returns updated KPI values
7. WHEN the dashboard page is loaded, THE Dashboard SHALL poll the KPI endpoint every 30 seconds
8. THE Dashboard SHALL display last update timestamp for KPI values


### Requirement 7: Dashboard Visualizations

**User Story:** As an Admin, I want interactive charts and graphs on the dashboard, so that I can understand trends and patterns visually.

#### Acceptance Criteria

1. THE Dashboard SHALL display a bar chart showing risk distribution across LOW, MEDIUM, HIGH, and CRITICAL levels
2. THE Dashboard SHALL display a line chart showing trend of high-risk students over the last 90 days
3. THE Dashboard SHALL display a pie chart showing intervention status distribution (DRAFT, PENDING, APPROVED, IN_PROGRESS, COMPLETED, CANCELLED)
4. THE Dashboard SHALL display a table showing top 10 schools by count of high-risk students
5. THE Dashboard SHALL display a table showing average attendance, academic, and behavior scores by region
6. WHEN a user clicks on a chart element, THE Dashboard SHALL navigate to filtered view showing relevant records
7. THE Dashboard SHALL use Chart.js library for rendering interactive charts
8. THE Dashboard SHALL display charts responsively on mobile and desktop screen sizes

### Requirement 8: Dashboard Alert System

**User Story:** As a Supervisor, I want to see critical alerts on the dashboard, so that I can respond quickly to urgent situations.

#### Acceptance Criteria

1. THE Dashboard SHALL display a list of students with CRITICAL risk level from last 7 days
2. THE Dashboard SHALL display a list of patients with 3 or more consecutive missed appointments
3. THE Dashboard SHALL display a list of intervention plans that are past target_end_date and still IN_PROGRESS
4. THE Dashboard SHALL display a list of referral actions that are PENDING for more than 7 days
5. WHEN a new critical alert is created, THE Dashboard SHALL display a notification badge with count
6. THE Dashboard SHALL allow users to dismiss alerts, which marks them as acknowledged in the database
7. THE Dashboard SHALL sort alerts by severity (CRITICAL first) and then by date (newest first)
8. THE Dashboard SHALL provide a link from each alert to the detailed record view

### Requirement 9: Dashboard Export Functionality

**User Story:** As an Admin, I want to export dashboard data, so that I can create reports for stakeholders.

#### Acceptance Criteria

1. THE Dashboard SHALL provide an export button for risk assessment data
2. WHEN a user clicks export to CSV, THE Dashboard SHALL generate a CSV file containing student_id, full_name, school_name, risk_level, overall_risk_score, and assessment_date
3. WHEN a user clicks export to PDF, THE Dashboard SHALL generate a PDF report containing KPIs, risk distribution chart, and top alerts
4. THE Dashboard SHALL include date range filter for exports (last 7 days, last 30 days, last 90 days, custom range)
5. THE Dashboard SHALL include region filter for exports
6. THE Dashboard SHALL log all export actions to AuditLog with user, export_type, date_range, and timestamp
7. THE Dashboard SHALL limit CSV exports to 1000 records maximum
8. WHEN an export is requested, THE Dashboard SHALL process it asynchronously and provide a download link when ready


### Requirement 10: Student Risk Prediction Model

**User Story:** As a data scientist, I want a trained ML model for predicting student disengagement risk, so that the system can identify at-risk students automatically.

#### Acceptance Criteria

1. THE AI_Engine SHALL provide a risk prediction model trained on attendance_rate, average_grade, behavior_incident_count, and consecutive_absences features
2. THE AI_Engine SHALL use scikit-learn RandomForestClassifier with 100 estimators
3. THE AI_Engine SHALL train the model on synthetic data with at least 1000 student records
4. THE AI_Engine SHALL achieve at least 80% accuracy on test set
5. THE AI_Engine SHALL save the trained model to ml_models/student_risk_model.pkl using joblib
6. THE AI_Engine SHALL provide a predict_student_risk function that accepts student_id and returns risk_level and confidence_score
7. WHEN a new RiskAssessment is created, THE AI_Engine SHALL calculate attendance_score, academic_score, and behavior_score from recent records
8. THE AI_Engine SHALL provide feature importance scores showing which factors contribute most to risk prediction

### Requirement 11: Patient Adherence Prediction Model

**User Story:** As a healthcare coordinator, I want a trained ML model for predicting patient adherence, so that the system can identify patients at risk of missing appointments.

#### Acceptance Criteria

1. THE AI_Engine SHALL provide an adherence prediction model trained on appointment_count, missed_count, consecutive_missed, days_since_last_appointment, and mood_score features
2. THE AI_Engine SHALL use scikit-learn GradientBoostingClassifier with 100 estimators
3. THE AI_Engine SHALL train the model on synthetic data with at least 500 patient records
4. THE AI_Engine SHALL achieve at least 75% accuracy on test set
5. THE AI_Engine SHALL save the trained model to ml_models/adherence_model.pkl using joblib
6. THE AI_Engine SHALL provide a predict_adherence_risk function that accepts patient_id and returns risk_level and confidence_score
7. WHEN a new AdherenceRecord is created, THE AI_Engine SHALL calculate adherence_rate and consecutive_missed from appointment history
8. THE AI_Engine SHALL provide a recommend_intervention function that suggests actions based on risk level (REMINDER for MEDIUM, FOLLOW_UP_CALL for HIGH, HOME_VISIT for CRITICAL)

### Requirement 12: Student Clustering for Grouping

**User Story:** As an educator, I want students grouped by similar characteristics, so that I can design targeted interventions for each group.

#### Acceptance Criteria

1. THE AI_Engine SHALL provide a clustering model using scikit-learn KMeans with 4 clusters
2. THE AI_Engine SHALL cluster students based on attendance_rate, average_grade, behavior_score, and socioeconomic_indicator features
3. THE AI_Engine SHALL assign each student to a cluster (HIGH_ACHIEVER, AT_RISK, STRUGGLING, or DISENGAGED)
4. THE AI_Engine SHALL save cluster assignments to database with cluster_id and cluster_label
5. THE AI_Engine SHALL provide a get_cluster_characteristics function that returns average feature values for each cluster
6. THE AI_Engine SHALL provide a get_cluster_recommendations function that returns suggested interventions for each cluster
7. WHEN clustering is run, THE AI_Engine SHALL update cluster assignments for all active students
8. THE Dashboard SHALL display cluster distribution chart showing count of students in each cluster


### Requirement 13: Model Training Scripts

**User Story:** As a system administrator, I want automated scripts for training ML models, so that I can retrain models with updated data.

#### Acceptance Criteria

1. THE AI_Engine SHALL provide a train_student_risk_model management command
2. THE AI_Engine SHALL provide a train_adherence_model management command
3. THE AI_Engine SHALL provide a run_clustering management command
4. WHEN a training command is executed, THE AI_Engine SHALL load data from database, split into train and test sets with 80-20 ratio, train the model, evaluate on test set, and save the trained model
5. THE AI_Engine SHALL log training metrics (accuracy, precision, recall, F1-score) to console and log file
6. THE AI_Engine SHALL save training metadata (timestamp, record_count, accuracy, feature_importance) to database
7. WHEN a model file already exists, THE AI_Engine SHALL create a backup with timestamp before overwriting
8. THE AI_Engine SHALL validate that training data has at least 100 records before training, and return an error if insufficient data

### Requirement 14: Real-time Prediction Integration

**User Story:** As an Operator, I want automatic risk predictions when I create records, so that I don't have to manually calculate risk scores.

#### Acceptance Criteria

1. WHEN a new Student is created with at least 5 attendance records and 3 grade records, THE System SHALL automatically create a RiskAssessment using the ML model
2. WHEN a new Appointment is marked as MISSED, THE System SHALL update the patient's AdherenceRecord and recalculate risk using the ML model
3. WHEN a RiskAssessment shows CRITICAL risk level, THE System SHALL automatically create a draft InterventionPlan assigned to the student's school supervisor
4. WHEN an AdherenceRecord shows HIGH or CRITICAL risk level, THE System SHALL automatically create a pending ReferralAction
5. THE System SHALL provide a recalculate_all_risks management command that recalculates risk assessments for all active students and patients
6. THE System SHALL log all automatic predictions to AuditLog with model_version, confidence_score, and prediction_result
7. WHEN a model prediction fails, THE System SHALL log the error and continue without blocking the user's action
8. THE System SHALL display model confidence score alongside risk level in the UI

### Requirement 15: Model Unit Tests

**User Story:** As a developer, I want comprehensive tests for model code, so that I can verify correctness of all model methods and properties.

#### Acceptance Criteria

1. THE Test_Suite SHALL test Student.full_name property returns first_name and last_name concatenated
2. THE Test_Suite SHALL test Student.age property calculates correct age from date_of_birth
3. THE Test_Suite SHALL test AttendanceRecord unique_together constraint prevents duplicate records for same student and date
4. THE Test_Suite SHALL test GradeRecord validation rejects grades below 0 or above 20
5. THE Test_Suite SHALL test RiskAssessment.risk_level is correctly assigned based on overall_risk_score thresholds
6. THE Test_Suite SHALL test Patient.full_name property returns first_name and last_name concatenated
7. THE Test_Suite SHALL test Appointment status transitions are valid (SCHEDULED can become CONFIRMED, COMPLETED, MISSED, or CANCELLED)
8. THE Test_Suite SHALL test AdherenceRecord.adherence_rate is calculated correctly as attended_appointments divided by total_appointments times 100

