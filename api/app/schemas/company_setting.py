from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanySettingBase(BaseModel):
    company_name: str
    company_logo_url: Optional[str] = None
    company_logo_data: Optional[str] = None
    primary_color: str = "#4A90E2"
    secondary_color: str = "#2C3E50"
    report_header_text: Optional[str] = None
    report_footer_text: Optional[str] = None
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"
    currency: str = "USD"
    is_active: bool = True


class CompanySettingCreate(CompanySettingBase):
    client_id: str


class CompanySettingUpdate(BaseModel):
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None
    company_logo_data: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    report_header_text: Optional[str] = None
    report_footer_text: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None


class CompanySettingResponse(CompanySettingBase):
    id: str
    client_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True
