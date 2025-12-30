# Team Assignment System Documentation

## Overview

The Team Assignment System is a comprehensive solution for managing project teams and entity assignments within the Worky project management platform. It provides role-based assignment validation, project-level team isolation, and complete audit trails for all assignment operations.

## Table of Contents

1. [Architecture](#architecture)
2. [Core Concepts](#core-concepts)
3. [API Reference](#api-reference)
4. [User Guide](#user-guide)
5. [Administrator Guide](#administrator-guide)
6. [Troubleshooting](#troubleshooting)
7. [Performance Optimization](#performance-optimization)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)              │
├─────────────────────────────────────────────────────────────┤
│  Team Management UI  │  Assignment UI  │  Notification UI   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│  Teams  │  Assignments  │  Validation  │  Notifications    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
├─────────────────────────────────────────────────────────────┤
│  TeamService  │  AssignmentService  │  ValidationService   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer (PostgreSQL)                   │
├─────────────────────────────────────────────────────────────┤
│  Teams  │  TeamMembers  │  Assignments  │  History  │ Cache │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

#### Core Tables

- **teams**: Project-level team definitions
- **team_members**: User-team associations with roles
- **assignments**: Entity-user assignment records
- **assignment_history**: Complete audit trail
- **notifications**: Assignment and team notifications
- **notification_preferences**: User notification settings

## Core Concepts

### Teams

Teams are project-scoped groups of users who can work on specific project elements. Each project can have one primary team, and team membership determines assignment eligibility.

**Key Properties:**
- Project-scoped isolation
- Role-based membership
- Hierarchical access control

### Assignments

Assignments link users to specific hierarchy elements (tasks, user stories, etc.) with defined roles and responsibilities.

**Assignment Types:**
- **owner**: Primary responsibility for high-level elements (Client, Program, Project) - Multiple owners allowed
- **assignee**: Work responsibility for lower-level elements (Use Case, User Story, Task, Subtask) - Team members only

### Assignment Rules Matrix

| Entity | Assignment Type | Who Handles | Selection Pool |
|--------|-----------------|-------------|----------------|
| Client | owner | Multiple Owners | Any eligible user (Admin, Owner, PM, Architect) |
| Program | owner | Multiple Owners | Any eligible user |
| Project | owner | Multiple Owners | Any eligible user |
| Use Case | assignee | Team Members | Only from Project Team |
| User Story | assignee | Team Members | Only from Project Team |
| Task | assignee | Team Members | Only from Project Team |
| Subtask | assignee | Team Members | Only from Project Team |

### Role-Based Validation

The system enforces strict role-based assignment rules:

| Entity Type | Allowed Roles | Assignment Type |
|-------------|---------------|-----------------|
| Client | Owner, Admin, Architect, Project Manager | owner |
| Program | Owner, Admin, Architect, Project Manager | owner |
| Project | Owner, Admin, Architect, Project Manager | owner |
| Use Case | Developer, Tester, Designer, Architect, Admin, Owner, PM, Lead, Manager, DevOps | assignee |
| User Story | Developer, Tester, Designer, Architect, Admin, Owner, PM, Lead, Manager, DevOps | assignee |
| Task | Developer, Tester, Designer, Architect, Admin, Owner, PM, Lead, Manager, DevOps | assignee |
| Subtask | Developer, Tester, Designer, Architect, Admin, Owner, PM, Lead, Manager, DevOps | assignee |

### Project Isolation

**Important**: For Use Cases, User Stories, Tasks, and Subtasks, only members of the project's assigned team can be assigned as assignees. This ensures:
- Data security and access control
- Clear project boundaries
- Proper resource allocation
- Work is done by team members only

## API Reference

### Team Management Endpoints

#### Create Team
```http
POST /api/v1/teams/
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "Development Team",
  "description": "Main development team for the project",
  "project_id": "PRJ-001"
}
```

#### Get Teams
```http
GET /api/v1/teams/?project_id=PRJ-001&page=1&per_page=20
Authorization: Bearer {token}
```

#### Add Team Member
```http
POST /api/v1/teams/{team_id}/members
Content-Type: application/json
Authorization: Bearer {token}

{
  "user_id": "USR-001",
  "role": "Developer"
}
```

### Assignment Management Endpoints

#### Create Assignment
```http
POST /api/v1/assignments/
Content-Type: application/json
Authorization: Bearer {token}

{
  "entity_type": "task",
  "entity_id": "TSK-001",
  "user_id": "USR-001",
  "assignment_type": "developer"
}
```

#### Get Assignments
```http
GET /api/v1/assignments/?user_id=USR-001&entity_type=task
Authorization: Bearer {token}
```

#### Bulk Assignment
```http
POST /api/v1/assignments/bulk
Content-Type: application/json
Authorization: Bearer {token}

{
  "assignments": [
    {
      "entity_type": "task",
      "entity_id": "TSK-001",
      "user_id": "USR-001",
      "assignment_type": "developer"
    },
    {
      "entity_type": "task",
      "entity_id": "TSK-002",
      "user_id": "USR-002",
      "assignment_type": "developer"
    }
  ]
}
```

### Validation Endpoints

#### Validate Assignment
```http
POST /api/v1/validation/assignment
Content-Type: application/json
Authorization: Bearer {token}

{
  "entity_type": "task",
  "entity_id": "TSK-001",
  "user_id": "USR-001",
  "assignment_type": "developer"
}
```

#### Get Eligible Users
```http
GET /api/v1/validation/eligible-users/task/TSK-001?assignment_type=developer
Authorization: Bearer {token}
```

## User Guide

### Managing Your Assignments

#### Viewing Your Assignments

1. Navigate to the **Assignments** page
2. Your current assignments are displayed by default
3. Use filters to view specific types or projects
4. Click on any assignment to see details

#### Assignment Notifications

You'll receive notifications when:
- You're assigned to a new task or user story
- Your assignment is removed or changed
- You're added to or removed from a team

#### Managing Notification Preferences

1. Go to **Settings** > **Notifications**
2. Configure preferences for each notification type:
   - Email notifications
   - In-app notifications
   - Push notifications (if enabled)

### Working with Teams

#### Viewing Team Information

1. Navigate to **Teams** page
2. Select your project team
3. View team members and their roles
4. See team workload distribution

#### Team Communication

- Use the team chat feature for coordination
- @mention team members in comments
- Share updates on assignment progress

## Administrator Guide

### Setting Up Teams

#### Creating Project Teams

1. Navigate to **Teams** > **Create Team**
2. Enter team name and description
3. Select the target project
4. Add initial team members with appropriate roles

#### Managing Team Members

1. Go to team details page
2. Use **Add Member** to invite users
3. Assign appropriate roles based on responsibilities:
   - **Owner**: Project leadership and high-level planning
   - **Developer**: Implementation and coding tasks
   - **Designer**: UI/UX and design tasks
   - **Tester**: Quality assurance and testing
   - **Contact Person**: Client communication (for client entities)

#### Role Assignment Guidelines

- **Owners/Architects**: Assign to programs, projects, use cases, user stories
- **Developers**: Assign to tasks and subtasks
- **Contact Persons**: Assign to client entities for communication
- **Designers**: Can be assigned to use cases and user stories for design work

### Bulk Operations

#### Bulk Team Setup

Use the migration service for bulk team creation:

```python
from app.services.migration_service import MigrationService

setup_config = [
    {
        "name": "Frontend Team",
        "description": "UI/UX development team",
        "project_id": "PRJ-001",
        "members": [
            {"user_id": "USR-001", "role": "Developer"},
            {"user_id": "USR-002", "role": "Designer"}
        ]
    }
]

migration_service = MigrationService(db)
result = await migration_service.bulk_team_setup(setup_config, admin_user)
```

#### Data Migration

Migrate existing assignments to the new system:

```python
result = await migration_service.migrate_existing_assignments(admin_user)
print(f"Created {result['teams_created']} teams")
print(f"Migrated {result['assignments_migrated']} assignments")
```

### Monitoring and Maintenance

#### Performance Monitoring

1. Use `/api/v1/performance/system/health` to check system health
2. Monitor cache statistics at `/api/v1/performance/cache/stats`
3. Review team workload at `/api/v1/performance/teams/{team_id}/workload`

#### Data Validation

Regularly validate assignment consistency:

```python
issues = await migration_service.validate_assignment_consistency()
if issues["orphaned_assignments"]:
    print("Found orphaned assignments that need attention")
```

## Troubleshooting

### Common Issues

#### Assignment Validation Failures

**Problem**: User cannot be assigned to an entity
**Causes**:
- User not in project team
- Role incompatible with entity type
- Assignment already exists

**Solutions**:
1. Verify user is team member: Check team membership
2. Check role compatibility: Ensure user role matches entity requirements
3. Remove existing assignment if reassigning

#### Team Access Issues

**Problem**: User cannot access team or assignments
**Causes**:
- Insufficient permissions
- Cross-project access attempt
- Inactive team membership

**Solutions**:
1. Verify user permissions and role
2. Check project team membership
3. Ensure team membership is active

#### Performance Issues

**Problem**: Slow assignment operations
**Causes**:
- Large team sizes
- Complex queries
- Cache misses

**Solutions**:
1. Enable query optimization
2. Use bulk operations for multiple assignments
3. Monitor and clear cache if needed

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| TEAM_001 | User not in team | Add user to project team |
| TEAM_002 | Invalid role for assignment | Check role compatibility |
| TEAM_003 | Assignment already exists | Remove existing or use update |
| TEAM_004 | Entity not found | Verify entity ID and type |
| TEAM_005 | Insufficient permissions | Check user role and permissions |

### Logging and Debugging

#### Enable Debug Logging

Set log level to DEBUG in configuration:
```python
LOG_LEVEL = "DEBUG"
```

#### Key Log Events

- `team_created`: New team creation
- `member_added`: Team member addition
- `assignment_created`: New assignment
- `assignment_removed`: Assignment removal
- `validation_failed`: Assignment validation failure

## Performance Optimization

### Caching Strategy

The system uses multi-level caching:

1. **Team Membership Cache**: 15-minute TTL
2. **Eligible Users Cache**: 10-minute TTL
3. **Assignment History Cache**: 5-minute TTL

#### Cache Management

```python
from app.services.cache_service import cache_service

# Clear specific cache
cache_service.invalidate_team_cache(team_id)

# Clear user-related cache
cache_service.invalidate_user_cache(user_id)

# Clear all cache
cache_service._cache.clear()
```

### Query Optimization

#### Use Optimized Queries

```python
from app.services.query_optimization_service import QueryOptimizationService

optimization_service = QueryOptimizationService(db)

# Optimized team members query
members = await optimization_service.get_team_members_optimized(team_id)

# Bulk team membership check
pairs = [(user_id, project_id) for user_id, project_id in user_project_pairs]
memberships = await optimization_service.bulk_check_team_membership(pairs)
```

#### Database Indexes

Ensure these indexes exist for optimal performance:

```sql
-- Team member lookups
CREATE INDEX idx_team_members_team_user ON team_members(team_id, user_id);
CREATE INDEX idx_team_members_user_active ON team_members(user_id, is_active);

-- Assignment lookups
CREATE INDEX idx_assignments_entity ON assignments(entity_type, entity_id);
CREATE INDEX idx_assignments_user ON assignments(assigned_to, is_active);

-- Project team lookups
CREATE INDEX idx_teams_project ON teams(project_id, is_active);
```

### Pagination

Use pagination for large datasets:

```python
from app.core.pagination import PaginationService, PaginationParams

pagination = PaginationParams(page=1, per_page=50)
result = await PaginationService.paginate_teams(db, base_query, pagination)
```

### Performance Benchmarks

Target performance metrics:

- Team creation: < 1 second
- Member addition: < 0.5 seconds
- Assignment creation: < 0.5 seconds
- Team member query (100 members): < 0.2 seconds
- Assignment validation: < 0.1 seconds

## Security Considerations

### Access Control

- All operations require authentication
- Role-based authorization for team management
- Project-level data isolation
- Input validation and sanitization

### Data Protection

- Encrypted data transmission (HTTPS)
- SQL injection prevention
- XSS protection in UI components
- Audit trails for all operations

### Best Practices

1. **Principle of Least Privilege**: Grant minimum necessary permissions
2. **Regular Access Reviews**: Periodically review team memberships
3. **Audit Monitoring**: Monitor assignment changes and access patterns
4. **Data Validation**: Always validate input data
5. **Error Handling**: Don't expose sensitive information in errors

## Integration Guide

### Frontend Integration

#### React Components

```typescript
import { TeamManagement } from '@/components/teams/TeamManagement';
import { AssignmentSelector } from '@/components/assignments/AssignmentSelector';

// Team management
<TeamManagement projectId="PRJ-001" />

// Assignment selection
<AssignmentSelector 
  entityType="task" 
  entityId="TSK-001" 
  onAssignmentChange={handleAssignmentChange}
/>
```

#### API Client

```typescript
import { apiClient } from '@/services/api';

// Create team
const team = await apiClient.post('/teams/', {
  name: 'Development Team',
  project_id: 'PRJ-001'
});

// Create assignment
const assignment = await apiClient.post('/assignments/', {
  entity_type: 'task',
  entity_id: 'TSK-001',
  user_id: 'USR-001',
  assignment_type: 'developer'
});
```

### Backend Integration

#### Service Usage

```python
from app.services.team_service import TeamService
from app.services.assignment_service import AssignmentService

# Create team
team_service = TeamService(db)
team = await team_service.create_team(
    name="Development Team",
    project_id="PRJ-001",
    current_user=current_user
)

# Create assignment
assignment_service = AssignmentService(db)
assignment = await assignment_service.assign_entity(
    entity_type="task",
    entity_id="TSK-001",
    user_id="USR-001",
    assignment_type="developer",
    current_user=current_user
)
```

## Changelog

### Version 1.0.0 (Current)

**Features:**
- Complete team management system
- Role-based assignment validation
- Project-level team isolation
- Comprehensive notification system
- Performance optimization with caching
- Full audit trail and history
- Bulk operations support
- Migration tools for existing data

**API Endpoints:**
- Teams: CRUD operations and member management
- Assignments: Creation, validation, and bulk operations
- Validation: Eligibility checking and rule validation
- Notifications: Preference management and delivery
- Performance: Monitoring and optimization tools

**Security:**
- Authentication and authorization
- Input validation and sanitization
- Cross-project isolation
- Audit logging

**Performance:**
- Query optimization
- Multi-level caching
- Pagination support
- Bulk operations

## Support

For technical support or questions:

1. Check this documentation first
2. Review the troubleshooting section
3. Check system logs for error details
4. Contact the development team with specific error messages and steps to reproduce

## License

This system is part of the Worky project management platform. All rights reserved.