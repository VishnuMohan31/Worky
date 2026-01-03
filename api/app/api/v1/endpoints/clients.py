"""
Client endpoints for the Worky API.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, distinct
from uuid import UUID

from app.db.base import get_db
from app.models.client import Client
from app.models.hierarchy import Project, Program
from app.models.user import User
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse, ClientList
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=ClientList)
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List clients. Admin sees all, others see only their client."""
    
    query = select(Client).where(Client.is_deleted == False)
    
    # Apply client-level filtering for non-admin users
    if current_user.role != "Admin":
        query = query.where(Client.id == current_user.client_id)
    
    # Count total
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    clients = result.scalars().all()
    
    return ClientList(
        clients=[ClientResponse.from_orm(client) for client in clients],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        has_more=(skip + limit) < total
    )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific client by ID."""
    
    result = await db.execute(
        select(Client).where(
            and_(
                Client.id == client_id,
                Client.is_deleted == False
            )
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise ResourceNotFoundException("Client", str(client_id))
    
    # Check access
    if current_user.role != "Admin" and client_id != current_user.client_id:
        raise AccessDeniedException()
    
    logger.log_activity(
        action="view_client",
        entity_type="client",
        entity_id=str(client_id)
    )
    
    return ClientResponse.from_orm(client)


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Create a new client (Admin only)."""
    
    # Generate client ID
    result = await db.execute(select(func.count(Client.id)))
    count = result.scalar() or 0
    client_id = f"CLI-{str(count + 1).zfill(3)}"
    
    client = Client(
        id=client_id,
        **client_data.dict(),
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(client)
    await db.commit()
    await db.refresh(client)
    
    logger.log_activity(
        action="create_client",
        entity_type="client",
        entity_id=str(client.id),
        client_name=client.name
    )
    
    return ClientResponse.from_orm(client)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Update a client (Admin only)."""
    
    result = await db.execute(
        select(Client).where(
            and_(
                Client.id == client_id,
                Client.is_deleted == False
            )
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise ResourceNotFoundException("Client", str(client_id))
    
    # Update fields
    for field, value in client_data.dict(exclude_unset=True).items():
        setattr(client, field, value)
    
    client.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(client)
    
    logger.log_activity(
        action="update_client",
        entity_type="client",
        entity_id=str(client_id)
    )
    
    return ClientResponse.from_orm(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Soft delete a client (Admin only)."""
    
    result = await db.execute(
        select(Client).where(
            and_(
                Client.id == client_id,
                Client.is_deleted == False
            )
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise ResourceNotFoundException("Client", str(client_id))
    
    client.is_deleted = True
    client.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_client",
        entity_type="client",
        entity_id=str(client_id)
    )


@router.get("/statistics/dashboard")
async def get_client_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get client statistics for dashboard.
    
    Returns:
    - Total number of clients
    - Number of clients with ongoing projects
    - Client details with project counts
    """
    
    # Base query for clients
    client_query = select(Client).where(Client.is_deleted == False)
    
    # Apply client-level filtering for non-admin users
    if current_user.role != "Admin":
        client_query = client_query.where(Client.id == current_user.client_id)
    
    # Get all clients
    result = await db.execute(client_query)
    clients = result.scalars().all()
    total_clients = len(clients)
    
    # Get clients with ongoing projects
    ongoing_statuses = ["Planning", "In Progress", "Active"]
    clients_with_ongoing = set()
    client_details = []
    
    for client in clients:
        # Count projects for this client (through programs)
        project_query = select(func.count(distinct(Project.id))).select_from(Project).join(
            Program, Project.program_id == Program.id
        ).where(
            and_(
                Program.client_id == client.id,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        )
        total_projects_result = await db.execute(project_query)
        total_projects = total_projects_result.scalar()
        
        # Count ongoing projects
        ongoing_query = select(func.count(distinct(Project.id))).select_from(Project).join(
            Program, Project.program_id == Program.id
        ).where(
            and_(
                Program.client_id == client.id,
                Project.status.in_(ongoing_statuses),
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        )
        ongoing_result = await db.execute(ongoing_query)
        ongoing_projects = ongoing_result.scalar()
        
        if ongoing_projects > 0:
            clients_with_ongoing.add(client.id)
        
        # Get latest project for this client (through programs)
        latest_project_query = select(Project).join(
            Program, Project.program_id == Program.id
        ).where(
            and_(
                Program.client_id == client.id,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        ).order_by(Project.created_at.desc()).limit(1)
        latest_project_result = await db.execute(latest_project_query)
        latest_project = latest_project_result.scalar_one_or_none()
        
        client_details.append({
            "id": str(client.id),
            "name": client.name,
            "description": client.short_description or "",
            "long_description": client.long_description or "",
            "industry": "",  # Not in model yet
            "contact_email": client.email or "",
            "contact_phone": client.phone or "",
            "is_active": client.is_active,
            "total_projects": total_projects,
            "ongoing_projects": ongoing_projects,
            "completed_projects": total_projects - ongoing_projects,
            "latest_project": {
                "id": str(latest_project.id),
                "name": latest_project.name,
                "status": latest_project.status,
                "created_at": latest_project.created_at.isoformat()
            } if latest_project else None,
            "created_at": client.created_at.isoformat(),
            "updated_at": client.updated_at.isoformat()
        })
    
    return {
        "total_clients": total_clients,
        "clients_with_ongoing_projects": len(clients_with_ongoing),
        "clients_with_no_projects": sum(1 for c in client_details if c["total_projects"] == 0),
        "total_projects_across_clients": sum(c["total_projects"] for c in client_details),
        "total_ongoing_projects": sum(c["ongoing_projects"] for c in client_details),
        "clients": client_details
    }
