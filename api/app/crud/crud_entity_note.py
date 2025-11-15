from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    
    def create(self, db: AsyncSession, *, obj_in: EntityNoteCreate, created_by: str) -> EntityNote:
        """Create a new note (synchronous for use within async context)"""
        db_obj = EntityNote(
            entity_type=obj_in.entity_type,
            entity_id=obj_in.entity_id,
            note_text=obj_in.note_text,
            created_by=created_by
        )
        db.add(db_obj)
        return db_obj


entity_note = CRUDEntityNote()
