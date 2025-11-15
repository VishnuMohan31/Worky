from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    clients,
    programs,
    projects,
    usecases,
    user_stories,
    tasks,
    subtasks,
    bugs,
    phases,
    dependencies,
    hierarchy,
    entity_notes
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
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(usecases.router, prefix="/usecases", tags=["usecases"])
api_router.include_router(user_stories.router, prefix="/user-stories", tags=["user-stories"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(subtasks.router, prefix="/subtasks", tags=["subtasks"])

# Bug tracking
api_router.include_router(bugs.router, prefix="/bugs", tags=["bugs"])

# Phase management
api_router.include_router(phases.router, prefix="/phases", tags=["phases"])

# Dependency management
api_router.include_router(dependencies.router, prefix="/dependencies", tags=["dependencies"])
