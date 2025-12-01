from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import re


class CommentBase(BaseModel):
    """Base schema for comments"""
    comment_text: str = Field(..., min_length=1)
    mentioned_users: Optional[str] = Field(None, description="JSON array of user IDs")
    attachments: Optional[str] = Field(None, description="JSON array of file paths")


class CommentCreate(CommentBase):
    """Schema for creating a comment"""
    
    @validator('mentioned_users')
    def validate_mentions_format(cls, v):
        """Validate that mentioned_users is valid JSON array format"""
        if v is None:
            return v
        # Basic validation - should be a JSON array string
        if not (v.startswith('[') and v.endswith(']')):
            raise ValueError('mentioned_users must be a JSON array string')
        return v


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    comment_text: Optional[str] = Field(None, min_length=1)
    attachments: Optional[str] = Field(None, description="JSON array of file paths")


class CommentResponse(CommentBase):
    """Schema for comment response"""
    id: str
    author_id: str
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    
    # Optional: Include author details
    author_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class BugCommentResponse(CommentResponse):
    """Schema for bug comment response"""
    bug_id: str
    
    class Config:
        from_attributes = True


class TestCaseCommentResponse(CommentResponse):
    """Schema for test case comment response"""
    test_case_id: str
    
    class Config:
        from_attributes = True


class CommentList(BaseModel):
    """Schema for paginated comment list"""
    comments: List[CommentResponse]
    total: int
    page: int = 1
    page_size: int = 50


# Bug Attachment Schemas
class AttachmentBase(BaseModel):
    """Base schema for attachment"""
    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_type: Optional[str] = Field(None, max_length=50)
    file_size: Optional[int] = None


class AttachmentCreate(AttachmentBase):
    """Schema for creating an attachment"""
    pass


class AttachmentResponse(AttachmentBase):
    """Schema for attachment response"""
    id: str
    uploaded_by: str
    uploaded_at: datetime
    is_deleted: bool = False
    
    # Optional: Include uploader details
    uploader_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class BugAttachmentBase(AttachmentBase):
    """Base schema for bug attachment"""
    pass


class BugAttachmentCreate(BugAttachmentBase):
    """Schema for creating a bug attachment"""
    bug_id: str


class BugAttachmentResponse(AttachmentResponse):
    """Schema for bug attachment response"""
    bug_id: str
    
    class Config:
        from_attributes = True


class BugAttachmentList(BaseModel):
    """Schema for paginated bug attachment list"""
    attachments: List[BugAttachmentResponse]
    total: int


# Bug Status History Schemas
class BugStatusHistoryResponse(BaseModel):
    """Schema for bug status history response"""
    id: str
    bug_id: str
    from_status: Optional[str] = None
    to_status: str
    resolution_type: Optional[str] = None
    notes: Optional[str] = None
    changed_by: str
    changed_at: datetime
    
    # Optional: Include changer details
    changer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class BugStatusHistoryList(BaseModel):
    """Schema for bug status history list"""
    history: List[BugStatusHistoryResponse]
    total: int
