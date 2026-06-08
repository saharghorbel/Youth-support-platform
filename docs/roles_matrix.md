# Roles and Permissions Matrix

## Role Definitions

### 1. Operator
**Purpose**: Front-line data entry and record management

**Responsibilities**:
- Enter student/patient records
- Update attendance, grades, appointments
- Record behavior notes and observations
- Upload bulk data files
- View assigned cases

**Limitations**:
- Cannot approve intervention plans
- Cannot modify risk thresholds
- Cannot access audit logs
- Cannot manage users

### 2. Supervisor/Counselor
**Purpose**: Case validation and intervention planning

**Responsibilities**:
- All Operator permissions, plus:
- Review risk assessments
- Validate flagged cases
- Create and approve intervention plans
- Assign cases to operators
- Generate case reports
- Document intervention outcomes

**Limitations**:
- Cannot modify system policies
- Cannot manage users
- Cannot access full audit logs
- Cannot change risk calculation rules

### 3. Admin/Manager
**Purpose**: System configuration and oversight

**Responsibilities**:
- All Supervisor permissions, plus:
- Manage users and roles
- Configure risk thresholds
- Access full audit logs
- Generate aggregate reports
- Export system data
- Modify system policies
- Monitor system health

**Limitations**:
- Cannot bypass audit logging
- Cannot delete audit records

## Permissions Matrix

| Action | Operator | Supervisor | Admin |
|--------|----------|------------|-------|
| **User Management** |
| View own profile | ✅ | ✅ | ✅ |
| Update own profile | ✅ | ✅ | ✅ |
| View other users | ❌ | ✅ | ✅ |
| Create users | ❌ | ❌ | ✅ |
| Modify user roles | ❌ | ❌ | ✅ |
| Delete users | ❌ | ❌ | ✅ |
| **Student/Patient Records** |
| Create records | ✅ | ✅ | ✅ |
| View records | ✅ | ✅ | ✅ |
| Update own records | ✅ | ✅ | ✅ |
| Update any records | ❌ | ✅ | ✅ |
| Delete records | ❌ | ❌ | ✅ |
| **Attendance & Grades** |
| Record attendance | ✅ | ✅ | ✅ |
| Record grades | ✅ | ✅ | ✅ |
| Modify attendance | ❌ | ✅ | ✅ |
| Modify grades | ❌ | ✅ | ✅ |
| **Risk Assessments** |
| View assessments | ✅ | ✅ | ✅ |
| Trigger assessment | ✅ | ✅ | ✅ |
| Override assessment | ❌ | ✅ | ✅ |
| Configure thresholds | ❌ | ❌ | ✅ |
| **Intervention Plans** |
| View plans | ✅ | ✅ | ✅ |
| Create plans | ❌ | ✅ | ✅ |
| Approve plans | ❌ | ✅ | ✅ |
| Update plans | ❌ | ✅ | ✅ |
| Close plans | ❌ | ✅ | ✅ |
| **Appointments & Follow-ups** |
| Schedule appointments | ✅ | ✅ | ✅ |
| Record follow-ups | ✅ | ✅ | ✅ |
| Cancel appointments | ❌ | ✅ | ✅ |
| Modify appointments | ❌ | ✅ | ✅ |
| **Reports & Analytics** |
| View case reports | ✅ | ✅ | ✅ |
| Generate case reports | ❌ | ✅ | ✅ |
| View aggregate reports | ❌ | ✅ | ✅ |
| Export data | ❌ | ✅ | ✅ |
| View KPI dashboard | ❌ | ✅ | ✅ |
| **Audit & Compliance** |
| View own audit logs | ✅ | ✅ | ✅ |
| View team audit logs | ❌ | ✅ | ✅ |
| View all audit logs | ❌ | ❌ | ✅ |
| Export audit logs | ❌ | ❌ | ✅ |
| **System Configuration** |
| View system settings | ❌ | ❌ | ✅ |
| Modify system settings | ❌ | ❌ | ✅ |
| Manage integrations | ❌ | ❌ | ✅ |
| System health monitoring | ❌ | ❌ | ✅ |

## State Transition Permissions

### Student/Patient Records

| From State | To State | Operator | Supervisor | Admin |
|------------|----------|----------|------------|-------|
| Draft | Active | ✅ | ✅ | ✅ |
| Active | Flagged | Auto | Auto | Auto |
| Flagged | Under Review | ❌ | ✅ | ✅ |
| Under Review | Intervention | ❌ | ✅ | ✅ |
| Intervention | Resolved | ❌ | ✅ | ✅ |
| Any | Archived | ❌ | ❌ | ✅ |

### Intervention Plans

| From State | To State | Operator | Supervisor | Admin |
|------------|----------|----------|------------|-------|
| Draft | Pending | ❌ | ✅ | ✅ |
| Pending | Approved | ❌ | ✅ | ✅ |
| Pending | Rejected | ❌ | ✅ | ✅ |
| Approved | In Progress | ❌ | ✅ | ✅ |
| In Progress | Completed | ❌ | ✅ | ✅ |
| Any | Cancelled | ❌ | ✅ | ✅ |

## Data Access Scope

### Operator
- **Own Records**: Full access to records they created
- **Team Records**: Read-only access to team members' records
- **Sensitive Fields**: Limited access (no guardian contact info editing)

### Supervisor
- **Department Records**: Full access to all records in their department
- **Cross-Department**: Read-only access with approval
- **Sensitive Fields**: Full access with audit logging

### Admin
- **All Records**: Full access to all records system-wide
- **Sensitive Fields**: Full access with audit logging
- **Deleted Records**: Can view soft-deleted records

## Audit Requirements by Role

### All Roles
- Login/logout events
- Record creation and updates
- Failed permission checks
- Data exports

### Supervisor
- Intervention plan approvals
- Risk assessment overrides
- Case assignments

### Admin
- User management actions
- System configuration changes
- Bulk data operations
- Audit log access

## Role Assignment Rules

1. **Default Role**: New users are assigned Operator role
2. **Role Changes**: Only Admins can change user roles
3. **Role Audit**: All role changes are logged with reason
4. **Multi-Role**: Users cannot have multiple roles simultaneously
5. **Role Deactivation**: Deactivated users retain role but lose all permissions

## Emergency Access

### Break-Glass Procedure
In critical situations, Admins can:
1. Grant temporary elevated permissions
2. Access must be logged with justification
3. Automatic notification to system owner
4. Time-limited (max 24 hours)
5. Post-incident review required

---

**Document Version**: 1.0
**Last Updated**: May 2026
**Status**: Approved
