from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class Notification(BaseModel):
    """Domain model for Notification"""
    id: UUID
    user_id: UUID
    title: str
    message: str
    type: str
    severity: Optional[str] = None
    related_id: Optional[UUID] = None
    related_type: Optional[str] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True