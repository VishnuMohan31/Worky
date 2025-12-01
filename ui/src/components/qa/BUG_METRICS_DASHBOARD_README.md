# Bug Metrics Dashboard

## Overview

The Bug Metrics Dashboard provides comprehensive analytics and visualizations for bug tracking and test execution metrics. It helps QA managers and project managers track quality trends and make data-driven decisions.

## Features

### 1. Bug Summary Metrics
- **Total Bugs**: Overall count of all bugs in the system
- **Open Bugs**: Count of bugs that are currently open (New, Open, In Progress, Reopened)
- **Closed Bugs**: Count of bugs that have been resolved (Closed, Verified, Rejected)
- **Resolution Rate**: Percentage of bugs that have been closed
- **Average Resolution Time**: Mean time (in days) to resolve bugs

### 2. Bug Distribution Charts

#### By Severity
Pie chart showing the distribution of bugs across severity levels:
- Blocker
- Critical
- Major
- Minor
- Trivial

#### By Priority
Pie chart showing the distribution of bugs across priority levels:
- P0 (Critical)
- P1 (High)
- P2 (Medium)
- P3 (Low)

### 3. Bug Trends
Line chart showing bug creation and resolution trends over the last 7 days (or custom date range). Helps identify:
- Periods of high bug discovery
- Resolution velocity
- Backlog growth or reduction

### 4. Bug Aging Report
Bar chart showing the distribution of open bugs by age:
- 0-7 days (recent bugs)
- 8-30 days (moderate age)
- 31-90 days (aging bugs)
- 90+ days (stale bugs)

Also displays average age by severity level to identify which severity levels have the oldest bugs.

### 5. Test Execution Metrics
- **Total Executions**: Count of all test case executions
- **Pass Rate**: Percentage of test executions that passed
- **Fail Rate**: Percentage of test executions that failed
- **Execution Coverage**: Percentage of test cases that have been executed

#### Test Execution Distribution
Pie chart showing the breakdown of test execution results:
- Passed
- Failed
- Blocked
- Skipped

#### Execution Coverage Progress Bar
Visual indicator of how many test cases have been executed vs. total test cases.

### 6. Test Velocity Trend
Line chart showing the number of test executions per day over the last 7 days. Helps track:
- Testing activity levels
- Team productivity
- Sprint testing progress

## Usage

### In Bug Lifecycle Page

1. Navigate to **QA > Bug Lifecycle** in the sidebar
2. Click the **📊 Metrics** tab in the header
3. The dashboard will load with metrics for all bugs
4. Use the hierarchy selector to filter metrics by:
   - Client
   - Program
   - Project
   - Use Case
   - User Story
   - Task
   - Subtask

### As a Standalone Component

```tsx
import BugMetricsDashboard from '../components/qa/BugMetricsDashboard'

// Use without filters (all bugs)
<BugMetricsDashboard />

// Use with hierarchy filter
<BugMetricsDashboard 
  hierarchyFilter={{
    projectId: 'proj-123',
    usecaseId: 'uc-456'
  }}
/>
```

## API Endpoints

The dashboard fetches data from the following API endpoints:

### Bug Summary Metrics
```
GET /api/v1/qa-metrics/bugs/summary
Query params: client_id, program_id, project_id, usecase_id, user_story_id, task_id, subtask_id
```

### Bug Trends
```
GET /api/v1/qa-metrics/bugs/trends
Query params: start_date, end_date, client_id, program_id, project_id, etc.
```

### Bug Aging Report
```
GET /api/v1/qa-metrics/bugs/aging
Query params: client_id, program_id, project_id, etc.
```

### Test Execution Metrics
```
GET /api/v1/qa-metrics/test-execution/summary
Query params: test_run_id, project_id, usecase_id, user_story_id, task_id
```

## Data Refresh

The dashboard automatically loads metrics when:
- The component mounts
- The hierarchy filter changes

To manually refresh, change the hierarchy filter or navigate away and back to the metrics view.

## Performance Considerations

- Metrics are calculated on-demand from the database
- For large datasets (1000+ bugs), initial load may take a few seconds
- Consider implementing caching for frequently accessed metrics
- The dashboard uses parallel API calls to minimize load time

## Future Enhancements

Potential improvements for future versions:
- Export metrics to PDF/Excel
- Custom date range selection for trends
- Comparison views (e.g., this sprint vs. last sprint)
- Real-time updates using WebSockets
- Customizable dashboard layouts
- Saved metric views/bookmarks
- Email reports scheduling
- SLA tracking and alerts

## Requirements Mapping

This component implements the following requirements from the QA Testing and Bug Management spec:

- **Requirement 8.7**: Bug metrics dashboard with KPIs
- **Requirement 9.7**: Test execution metrics (pass rate, fail rate, coverage)
- **Requirement 12.1**: Bug summary metrics
- **Requirement 12.2**: Bug density and distribution
- **Requirement 12.3**: Bug trend analysis
- **Requirement 12.4**: Bug aging reports
- **Requirement 12.5**: Bug distribution by severity/priority
- **Requirement 12.6**: Mean time to resolution (MTTR)
- **Requirement 12.11**: Test execution coverage and trends
