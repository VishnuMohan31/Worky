from sqlalchemy.orm import Session
from typing import Optional
from app.crud.base import CRUDBase
from app.models.company_setting import CompanySetting
from app.schemas.company_setting import CompanySettingCreate, CompanySettingUpdate


class CRUDCompanySetting(CRUDBase[CompanySetting, CompanySettingCreate, CompanySettingUpdate]):
    def get_by_client(self, db: Session, *, client_id: str) -> Optional[CompanySetting]:
        """Get company settings for a client"""
        return db.query(CompanySetting).filter(
            CompanySetting.client_id == client_id
        ).first()


company_setting = CRUDCompanySetting(CompanySetting)
