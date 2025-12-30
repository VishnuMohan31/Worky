from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    clients,
    programs,
    projects,
    usecases,
    user_stories,
    userstorys_alias,
    tasks,
    subtasks,
    bugs,
    phases,
    dependencies,
    hierarchy,
    entity_notes,
    users,
    test_cases,
    test_runs,
    test_executions,
    comments,
    qa_metrics,
    sprints,
    organizations,
    todos,
    adhoc_notes,
    chat,
    reports,
    audit_logs,
    teams,
    assignments,
    validation,
    decisions
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Unified Hierarchy Management (new consolidated endpoints)
api_router.include_router(hierarchy.router, prefix="/hierarchy", tags=["hierarchy"])

# Entity Notes (comments on any hierarchy element)
api_router.include_router(entity_notes.router, prefix="/hierarchy", tags=["entity-notes"])

# Legacy Hierarchy endpoints (kept for backward compatibility)
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(programs.router, prefix="/programs", tags=["programs"])
# Sprint management (must be before projects router to avoid route conflicts)
api_router.include_router(sprints.router, tags=["sprints"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(usecases.router, prefix="/usecases", tags=["usecases"])
api_router.include_router(user_stories.router, prefix="/user-stories", tags=["user-stories"])
api_router.include_router(userstorys_alias.router, prefix="/userstorys", tags=["user-stories-alias"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(subtasks.router, prefix="/subtasks", tags=["subtasks"])

# Bug tracking
api_router.include_router(bugs.router, prefix="/bugs", tags=["bugs"])

# QA - Test case management
api_router.include_router(test_cases.router, prefix="/test-cases", tags=["test-cases"])

# QA - Test run management
api_router.include_router(test_runs.router, prefix="/test-runs", tags=["test-runs"])

# QA - Test execution management
api_router.include_router(test_executions.router, prefix="/test-executions", tags=["test-executions"])

# QA - Comments (for bugs and test cases)
api_router.include_router(comments.router, tags=["comments"])

# QA - Metrics and analytics
api_router.include_router(qa_metrics.router, prefix="/qa-metrics", tags=["qa-metrics"])

# Phase management
api_router.include_router(phases.router, prefix="/phases", tags=["phases"])

# Dependency management
api_router.include_router(dependencies.router, prefix="/dependencies", tags=["dependencies"])

# User management
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Organizations
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])

# TODO feature - Personal work organization
api_router.include_router(todos.router, tags=["todos"])

# ADHOC notes - Standalone sticky notes
api_router.include_router(adhoc_notes.router, tags=["adhoc-notes"])

# Chat Assistant - Natural language query interface
api_router.include_router(chat.router, tags=["chat"])

# Reports - Generate and export reports in PDF/CSV
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# Audit Logs - Track changes and access history
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])

# Team Management - Project-based team organization
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])

# Assignment Management - Entity-user assignment tracking
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])

# Validation - Assignment and team validation utilities
api_router.include_router(validation.router, prefix="/validation", tags=["validation"])

# Decisions - Decision tracking and management system
api_router.include_router(decisions.router, prefix="/decisions", tags=["decisions"])

# Notifications - Assignment and team notification system
from app.api.v1.endpoints import notifications
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

# Performance - Performance monitoring and optimization (temporarily disabled due to missing psutil dependency)
# from app.api.v1.endpoints import performance
# api_router.include_router(performance.router, prefix="/performance", tags=["performance"])
