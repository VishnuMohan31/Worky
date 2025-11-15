from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models.bug import Bug
from app.schemas.bug import BugCreate, BugUpdate


class CRUDBug(CRUDBase[Bug, BugCreate, BugUpdate]):
    def get_by_entity(
        self, 
        db: Session, 
        *, 
        entity_type: str, 
        entity_id: str,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        query = db.query(Bug).filter(
            Bug.entity_type == entity_type,
            Bug.entity_id == entity_id,
            Bug.is_deleted == False
        )
        
        if severity:
            query = query.filter(Bug.severity == severity)
        if status:
            query = query.filter(Bug.status == status)
            
        return query.offset(skip).limit(limit).all()
    
    def get_by_assignee(self, db: Session, *, assignee_id: str, skip: int = 0, limit: int = 100) -> List[Bug]:
        return db.query(Bug).filter(
            Bug.assigned_to == assignee_id,
            Bug.is_deleted == False
        ).offset(skip).limit(limit).all()


bug = CRUDBug(Bug)
