from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.chat import Reminder
from app.schemas.chat import ReminderCreate, ReminderUpdate


class CRUDReminder(CRUDBase[Reminder, ReminderCreate, ReminderUpdate]):
    """CRUD operations for Reminder model"""
    
    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Reminder]:
        """
        Get all reminders for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of reminders for the user
        """
        query = select(Reminder).where(
            Reminder.user_id == user_id
        ).order_by(Reminder.remind_at).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_pending_reminders(
        self,
        db: AsyncSession,
        *,
        user_id: Optional[str] = None,
        before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Reminder]:
        """
        Get pending (unsent) reminders that are due.
        
        Args:
            db: Database session
            user_id: Optional user ID to filter by specific user
            before: Optional datetime to get reminders due before this time
                   (defaults to current time)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of pending reminders
        """
        if before is None:
            before = datetime.now()
        
        # Build base query for unsent reminders due before specified time
        conditions = [
            Reminder.is_sent == False,
            Reminder.remind_at <= before
        ]
        
        # Add user filter if specified
        if user_id:
            conditions.append(Reminder.user_id == user_id)
        
        query = select(Reminder).where(
            and_(*conditions)
        ).order_by(Reminder.remind_at).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_entity(
        self,
        db: AsyncSession,
        *,
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Reminder]:
        """
        Get reminders for a specific entity.
        
        Args:
            db: Database session
            entity_type: Type of entity ("task", "bug", "project")
            entity_id: ID of the entity
            user_id: Optional user ID to filter by specific user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of reminders for the entity
        """
        conditions = [
            Reminder.entity_type == entity_type,
            Reminder.entity_id == entity_id
        ]
        
        if user_id:
            conditions.append(Reminder.user_id == user_id)
        
        query = select(Reminder).where(
            and_(*conditions)
        ).order_by(Reminder.remind_at).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: ReminderCreate,
        user_id: str
    ) -> Reminder:
        """
        Create a new reminder.
        
        Args:
            db: Database session
            obj_in: Reminder data
            user_id: User ID of the owner
            
        Returns:
            Created reminder
        """
        obj_in_data = obj_in.model_dump()
        obj_in_data["user_id"] = user_id
        
        db_obj = Reminder(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def mark_as_sent(
        self,
        db: AsyncSession,
        *,
        reminder_id: str
    ) -> Optional[Reminder]:
        """
        Mark a reminder as sent.
        
        Args:
            db: Database session
            reminder_id: Reminder ID
            
        Returns:
            Updated reminder or None if not found
        """
        query = select(Reminder).where(Reminder.id == reminder_id)
        result = await db.execute(query)
        reminder = result.scalar_one_or_none()
        
        if not reminder:
            return None
        
        reminder.is_sent = True
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)
        return reminder
    
    async def mark_multiple_as_sent(
        self,
        db: AsyncSession,
        *,
        reminder_ids: List[str]
    ) -> int:
        """
        Mark multiple reminders as sent in a batch operation.
        
        Args:
            db: Database session
            reminder_ids: List of reminder IDs to mark as sent
            
        Returns:
            Number of reminders updated
        """
        if not reminder_ids:
            return 0
        
        query = select(Reminder).where(Reminder.id.in_(reminder_ids))
        result = await db.execute(query)
        reminders = result.scalars().all()
        
        count = 0
        for reminder in reminders:
            reminder.is_sent = True
            db.add(reminder)
            count += 1
        
        await db.commit()
        return count
    
    async def delete_reminder(
        self,
        db: AsyncSession,
        *,
        reminder_id: str,
        user_id: str
    ) -> Optional[Reminder]:
        """
        Delete a reminder (hard delete since reminders don't have is_deleted field).
        Only the owner can delete their reminder.
        
        Args:
            db: Database session
            reminder_id: Reminder ID
            user_id: User ID for ownership verification
            
        Returns:
            Deleted reminder or None if not found or not owned by user
        """
        query = select(Reminder).where(
            and_(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id
            )
        )
        result = await db.execute(query)
        reminder = result.scalar_one_or_none()
        
        if not reminder:
            return None
        
        await db.delete(reminder)
        await db.commit()
        return reminder
    
    async def get_upcoming_reminders(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        hours_ahead: int = 24,
        skip: int = 0,
        limit: int = 100
    ) -> List[Reminder]:
        """
        Get upcoming reminders for a user within a specified time window.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            hours_ahead: Number of hours to look ahead (default 24)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of upcoming reminders
        """
        from datetime import timedelta
        
        now = datetime.now()
        future_time = now + timedelta(hours=hours_ahead)
        
        query = select(Reminder).where(
            and_(
                Reminder.user_id == user_id,
                Reminder.is_sent == False,
                Reminder.remind_at >= now,
                Reminder.remind_at <= future_time
            )
        ).order_by(Reminder.remind_at).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()


# Create singleton instance
reminder = CRUDReminder(Reminder)
