from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.models.entity_note import EntityNote
from app.schemas.entity_note import EntityNoteCreate


class CRUDEntityNote:
    async def get_by_entity(
        self, 
        db: AsyncSession, 
        *, 
        entity_type: str, 
        entity_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[EntityNote]:
        """Get notes for an entity, ordered by most recent first"""
        query = select(EntityNote).where(
            EntityNote.entity_type == entity_type,
            EntityNote.entity_id == entity_id
        ).order_by(EntityNote.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _generate_id(self, db: AsyncSession) -> str:
        """Generate a unique ID for a note"""
        # Get the count of existing notes
        result = await db.execute(select(func.count(EntityNote.id)))
        count = result.scalar() or 0
        
        # Generate ID in format NOTE-XXX
        new_id = f"NOTE-{str(count + 1).zfill(3)}"
        
        # Check if ID already exists (in case of concurrent inserts)
        result = await db.execute(select(EntityNote).where(EntityNote.id == new_id))
        if result.scalar_one_or_none():
            # If exists, try with timestamp
            import time
            new_id = f"NOTE-{int(time.time() * 1000) % 1000000}"
        
        return new_id
    
    async def create(self, db: AsyncSession, *, obj_in: EntityNoteCreate, created_by: str) -> EntityNote:
        """Create a new note"""
        note_id = await self._generate_id(db)
        
        db_obj = EntityNote(
            id=note_id,
            entity_type=obj_in.entity_type,
            entity_id=obj_in.entity_id,
            note_text=obj_in.note_text,
            created_by=created_by
        )
        db.add(db_obj)
        return db_obj


entity_note = CRUDEntityNote()
