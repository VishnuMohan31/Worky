"""
Dependency management endpoints for the Worky API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, or_
from typing import List
from uuid import UUID

from app.db.base import get_db
from app.models.dependency import Dependency
from app.models.user import User
from app.schemas.dependency import (
    DependencyCreate,
    DependencyUpdate,
    DependencyResponse,
    DependencyWithDetails,
    DependencyBulkCreate,
    DependencyTreeNode,
    EntityType
)
from app.core.security import get_current_user
from app.services.dependency_service import DependencyService

router = APIRouter()


@router.post("/", response_model=DependencyResponse, status_code=status.HTTP_201_CREATED)
async def create_dependency(
    dependency: DependencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new dependency between two entities.
    
    Supports all hierarchy levels: Program, Project, Usecase, UserStory, Task, Subtask
    Validates for circular dependencies and scheduling conflicts.
    """
    service = DependencyService(db)
    
    # Check for circular dependency before creating
    if await service.validate_circular_dependency(
        dependency.entity_type.value,
        dependency.entity_id,
        dependency.depends_on_type.value,
        dependency.depends_on_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creating this dependency would create a circular dependency"
        )
    
    # Check for scheduling conflicts
    conflict = await service.validate_scheduling_conflicts(
        dependency.entity_type.value,
        dependency.entity_id,
        dependency.depends_on_type.value,
        dependency.depends_on_id,
        dependency.dependency_type.value
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scheduling conflict: {conflict}"
        )
    
    # Check if dependency already exists
    existing = await db.execute(
        select(Dependency).where(
            and_(
                Dependency.entity_type == dependency.entity_type.value,
                Dependency.entity_id == dependency.entity_id,
                Dependency.depends_on_type == dependency.depends_on_type.value,
                Dependency.depends_on_id == dependency.depends_on_id
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dependency already exists"
        )
    
    # Create new dependency
    db_dependency = Dependency(
        entity_type=dependency.entity_type.value,
        entity_id=dependency.entity_id,
        depends_on_type=dependency.depends_on_type.value,
        depends_on_id=dependency.depends_on_id,
        dependency_type=dependency.dependency_type.value
    )
    
    db.add(db_dependency)
    await db.commit()
    await db.refresh(db_dependency)
    
    return db_dependency


@router.post("/bulk", response_model=List[DependencyResponse], status_code=status.HTTP_201_CREATED)
async def create_dependencies_bulk(
    bulk_data: DependencyBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create multiple dependencies at once.
    
    Validates all dependencies before creating any to ensure atomicity.
    Checks for circular dependencies and scheduling conflicts.
    """
    service = DependencyService(db)
    created_dependencies = []
    
    # Validate all dependencies first
    for dep in bulk_data.dependencies:
        # Check for circular dependency
        if await service.validate_circular_dependency(
            dep.entity_type.value,
            dep.entity_id,
            dep.depends_on_type.value,
            dep.depends_on_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dependency from {dep.entity_type}:{dep.entity_id} to {dep.depends_on_type}:{dep.depends_on_id} would create a circular dependency"
            )
        
        # Check for scheduling conflicts
        conflict = await service.validate_scheduling_conflicts(
            dep.entity_type.value,
            dep.entity_id,
            dep.depends_on_type.value,
            dep.depends_on_id,
            dep.dependency_type.value
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scheduling conflict in dependency {dep.entity_type}:{dep.entity_id} -> {dep.depends_on_type}:{dep.depends_on_id}: {conflict}"
            )
    
    # Create all dependencies
    for dep in bulk_data.dependencies:
        db_dependency = Dependency(
            entity_type=dep.entity_type.value,
            entity_id=dep.entity_id,
            depends_on_type=dep.depends_on_type.value,
            depends_on_id=dep.depends_on_id,
            dependency_type=dep.dependency_type.value
        )
        db.add(db_dependency)
        created_dependencies.append(db_dependency)
    
    await db.commit()
    
    # Refresh all created dependencies
    for dep in created_dependencies:
        await db.refresh(dep)
    
    return created_dependencies


@router.get("/{dependency_id}", response_model=DependencyResponse)
async def get_dependency(
    dependency_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific dependency by ID."""
    result = await db.execute(
        select(Dependency).where(Dependency.id == dependency_id)
    )
    dependency = result.scalar_one_or_none()
    
    if not dependency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency not found"
        )
    
    return dependency


@router.put("/{dependency_id}", response_model=DependencyResponse)
async def update_dependency(
    dependency_id: str,
    dependency_update: DependencyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a dependency's type.
    
    Only the dependency_type can be updated (e.g., from finish_to_start to start_to_start).
    """
    result = await db.execute(
        select(Dependency).where(Dependency.id == dependency_id)
    )
    dependency = result.scalar_one_or_none()
    
    if not dependency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency not found"
        )
    
    if dependency_update.dependency_type:
        dependency.dependency_type = dependency_update.dependency_type.value
    
    await db.commit()
    await db.refresh(dependency)
    
    return dependency


@router.delete("/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dependency(
    dependency_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a dependency."""
    result = await db.execute(
        select(Dependency).where(Dependency.id == dependency_id)
    )
    dependency = result.scalar_one_or_none()
    
    if not dependency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency not found"
        )
    
    await db.delete(dependency)
    await db.commit()
    
    return None


@router.delete("/entity/{entity_type}/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity_dependencies(
    entity_type: EntityType,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete all dependencies for a specific entity.
    
    Removes both dependencies where the entity depends on others
    and where others depend on this entity.
    """
    await db.execute(
        delete(Dependency).where(
            or_(
                and_(
                    Dependency.entity_type == entity_type.value,
                    Dependency.entity_id == entity_id
                ),
                and_(
                    Dependency.depends_on_type == entity_type.value,
                    Dependency.depends_on_id == entity_id
                )
            )
        )
    )
    await db.commit()
    
    return None


@router.post("/validate", status_code=status.HTTP_200_OK)
async def validate_dependency(
    dependency: DependencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate a dependency without creating it.
    
    Returns validation results including circular dependency check and scheduling conflicts.
    """
    service = DependencyService(db)
    
    # Check for circular dependency
    is_circular = await service.validate_circular_dependency(
        dependency.entity_type.value,
        dependency.entity_id,
        dependency.depends_on_type.value,
        dependency.depends_on_id
    )
    
    # Check for scheduling conflicts
    scheduling_conflict = await service.validate_scheduling_conflicts(
        dependency.entity_type.value,
        dependency.entity_id,
        dependency.depends_on_type.value,
        dependency.depends_on_id,
        dependency.dependency_type.value
    )
    
    return {
        "valid": not is_circular and not scheduling_conflict,
        "circular_dependency": is_circular,
        "scheduling_conflict": scheduling_conflict,
        "message": (
            "Dependency is valid" if not is_circular and not scheduling_conflict
            else "Circular dependency detected" if is_circular
            else f"Scheduling conflict: {scheduling_conflict}"
        )
    }


@router.get("/entity/{entity_type}/{entity_id}/validate-chain")
async def validate_dependency_chain(
    entity_type: EntityType,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate the entire dependency chain for an entity.
    
    Returns all validation errors found in the dependency chain.
    """
    service = DependencyService(db)
    errors = await service.validate_dependency_chain(entity_type.value, entity_id)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "message": "Dependency chain is valid" if len(errors) == 0 else f"Found {len(errors)} validation error(s)"
    }


@router.get("/entity/{entity_type}/{entity_id}/critical-path", response_model=List[DependencyResponse])
async def get_critical_path(
    entity_type: EntityType,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the critical path for an entity's dependency chain.
    
    The critical path is the longest sequence of dependent tasks.
    """
    service = DependencyService(db)
    critical_path = await service.get_critical_path(entity_type.value, entity_id)
    
    return critical_path


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[DependencyResponse])
async def get_entity_dependencies(
    entity_type: EntityType,
    entity_id: str,
    direction: str = "both",  # "outgoing", "incoming", or "both"
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all dependencies for a specific entity.
    
    - direction="outgoing": Get entities this entity depends on
    - direction="incoming": Get entities that depend on this entity
    - direction="both": Get all dependencies (default)
    """
    if direction not in ["outgoing", "incoming", "both"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Direction must be 'outgoing', 'incoming', or 'both'"
        )
    
    dependencies = []
    
    # Get outgoing dependencies (this entity depends on others)
    if direction in ["outgoing", "both"]:
        result = await db.execute(
            select(Dependency).where(
                and_(
                    Dependency.entity_type == entity_type.value,
                    Dependency.entity_id == entity_id
                )
            )
        )
        dependencies.extend(result.scalars().all())
    
    # Get incoming dependencies (others depend on this entity)
    if direction in ["incoming", "both"]:
        result = await db.execute(
            select(Dependency).where(
                and_(
                    Dependency.depends_on_type == entity_type.value,
                    Dependency.depends_on_id == entity_id
                )
            )
        )
        dependencies.extend(result.scalars().all())
    
    return dependencies


@router.get("/entity/{entity_type}/{entity_id}/tree")
async def get_dependency_tree(
    entity_type: EntityType,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the complete dependency tree/graph for an entity.
    
    Returns a hierarchical structure showing all dependencies and dependents.
    """
    service = DependencyService(db)
    
    # Get the complete dependency chain
    chain = await service.get_dependency_chain(entity_type.value, entity_id)
    
    # Build tree structure
    tree = await _build_dependency_tree(db, entity_type.value, entity_id, chain)
    
    return tree


@router.get("/entity/{entity_type}/{entity_id}/graph")
async def get_dependency_graph(
    entity_type: EntityType,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the dependency graph for an entity in a format suitable for visualization.
    
    Returns nodes and edges for graph visualization libraries.
    """
    service = DependencyService(db)
    
    # Get all dependencies in the chain
    chain = await service.get_dependency_chain(entity_type.value, entity_id)
    
    # Build nodes and edges
    nodes = {}
    edges = []
    
    # Add root node
    root_entity = await _get_entity_details(db, entity_type.value, entity_id)
    nodes[f"{entity_type.value}:{entity_id}"] = {
        "id": str(entity_id),
        "type": entity_type.value,
        "name": root_entity.get("name", "Unknown"),
        "is_root": True
    }
    
    # Process all dependencies
    for dep in chain:
        # Add entity node
        entity_key = f"{dep.entity_type}:{dep.entity_id}"
        if entity_key not in nodes:
            entity_details = await _get_entity_details(db, dep.entity_type, dep.entity_id)
            nodes[entity_key] = {
                "id": str(dep.entity_id),
                "type": dep.entity_type,
                "name": entity_details.get("name", "Unknown"),
                "is_root": False
            }
        
        # Add depends_on node
        depends_on_key = f"{dep.depends_on_type}:{dep.depends_on_id}"
        if depends_on_key not in nodes:
            depends_on_details = await _get_entity_details(db, dep.depends_on_type, dep.depends_on_id)
            nodes[depends_on_key] = {
                "id": str(dep.depends_on_id),
                "type": dep.depends_on_type,
                "name": depends_on_details.get("name", "Unknown"),
                "is_root": False
            }
        
        # Add edge
        edges.append({
            "id": str(dep.id),
            "source": str(dep.entity_id),
            "target": str(dep.depends_on_id),
            "type": dep.dependency_type,
            "label": dep.dependency_type.replace("_", " ").title()
        })
    
    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }


async def _build_dependency_tree(
    db: AsyncSession,
    entity_type: str,
    entity_id: str,
    all_dependencies: List[Dependency]
) -> dict:
    """Build a hierarchical tree structure from dependencies"""
    entity_details = await _get_entity_details(db, entity_type, entity_id)
    
    # Get direct dependencies
    direct_deps = [
        dep for dep in all_dependencies
        if dep.entity_type == entity_type and dep.entity_id == entity_id
    ]
    
    # Get direct dependents
    direct_dependents = [
        dep for dep in all_dependencies
        if dep.depends_on_type == entity_type and dep.depends_on_id == entity_id
    ]
    
    tree = {
        "id": str(entity_id),
        "type": entity_type,
        "name": entity_details.get("name", "Unknown"),
        "dependencies": [],
        "dependents": []
    }
    
    # Recursively build dependencies
    for dep in direct_deps:
        child_tree = await _build_dependency_tree(
            db,
            dep.depends_on_type,
            dep.depends_on_id,
            all_dependencies
        )
        child_tree["dependency_type"] = dep.dependency_type
        tree["dependencies"].append(child_tree)
    
    # Add dependents (non-recursive to avoid infinite loops)
    for dep in direct_dependents:
        dependent_details = await _get_entity_details(db, dep.entity_type, dep.entity_id)
        tree["dependents"].append({
            "id": str(dep.entity_id),
            "type": dep.entity_type,
            "name": dependent_details.get("name", "Unknown"),
            "dependency_type": dep.dependency_type
        })
    
    return tree


async def _get_entity_details(db: AsyncSession, entity_type: str, entity_id: str) -> dict:
    """Get basic details (name, etc.) for an entity"""
    from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask
    
    model_map = {
        "Program": Program,
        "Project": Project,
        "Usecase": Usecase,
        "UserStory": UserStory,
        "Task": Task,
        "Subtask": Subtask
    }
    
    model = model_map.get(entity_type)
    if not model:
        return {"name": "Unknown"}
    
    result = await db.execute(
        select(model).where(model.id == entity_id)
    )
    entity = result.scalar_one_or_none()
    
    if not entity:
        return {"name": "Unknown"}
    
    # Get name field (different entities use different field names)
    name = getattr(entity, 'name', None) or getattr(entity, 'title', None) or "Unknown"
    
    return {
        "name": name,
        "id": str(entity.id),
        "type": entity_type
    }
