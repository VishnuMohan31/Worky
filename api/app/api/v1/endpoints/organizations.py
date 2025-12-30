"""
Organization endpoints for the Worky API.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.db.base import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationList
)
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=OrganizationList)
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: bool = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List organizations. Admin sees all, others see only active ones."""
    
    query = select(Organization).where(Organization.is_deleted == False)
    
    # Apply active filter if provided
    if is_active is not None:
        query = query.where(Organization.is_active == is_active)
    
    # Non-admin users only see active organizations
    if current_user.role != "Admin":
        query = query.where(Organization.is_active == True)
    
    # Count total
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    organizations = result.scalars().all()
    
    return OrganizationList(
        organizations=[OrganizationResponse.from_orm(org) for org in organizations],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        has_more=(skip + limit) < total
    )


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific organization by ID."""
    
    result = await db.execute(
        select(Organization).where(
            and_(
                Organization.id == organization_id,
                Organization.is_deleted == False
            )
        )
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise ResourceNotFoundException("Organization", str(organization_id))
    
    # Non-admin users can only see active organizations
    if current_user.role != "Admin" and not organization.is_active:
        raise AccessDeniedException()
    
    logger.log_activity(
        action="view_organization",
        entity_type="organization",
        entity_id=str(organization_id)
    )
    
    return OrganizationResponse.from_orm(organization)


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Create a new organization (Admin only)."""
    
    # Generate organization ID
    result = await db.execute(select(func.count(Organization.id)))
    count = result.scalar() or 0
    organization_id = f"ORG-{str(count + 1).zfill(3)}"
    
    organization = Organization(
        id=organization_id,
        **organization_data.dict(),
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(organization)
    await db.commit()
    await db.refresh(organization)
    
    logger.log_activity(
        action="create_organization",
        entity_type="organization",
        entity_id=str(organization.id),
        organization_name=organization.name
    )
    
    return OrganizationResponse.from_orm(organization)


@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str,
    organization_data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Update an organization (Admin only)."""
    
    result = await db.execute(
        select(Organization).where(
            and_(
                Organization.id == organization_id,
                Organization.is_deleted == False
            )
        )
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise ResourceNotFoundException("Organization", str(organization_id))
    
    # Update fields
    update_data = organization_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)
    
    organization.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(organization)
    
    logger.log_activity(
        action="update_organization",
        entity_type="organization",
        entity_id=str(organization_id)
    )
    
    return OrganizationResponse.from_orm(organization)


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Soft delete an organization (Admin only)."""
    
    result = await db.execute(
        select(Organization).where(
            and_(
                Organization.id == organization_id,
                Organization.is_deleted == False
            )
        )
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise ResourceNotFoundException("Organization", str(organization_id))
    
    organization.is_deleted = True
    organization.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_organization",
        entity_type="organization",
        entity_id=str(organization_id)
    )

