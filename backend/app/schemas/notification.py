from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class NotificationCreate(BaseModel):
    """Schema for creating notification (internal use)"""
    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: str = Field(..., pattern="^(anomaly|prediction|server|system)$")
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    related_id: Optional[str] = None
    related_type: Optional[str] = Field(None, pattern="^(anomaly|prediction|server)$")


class NotificationResponse(BaseModel):
    """Schema for notification in responses"""
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


class NotificationListResponse(BaseModel):
    """Schema for paginated list of notifications"""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationMarkRead(BaseModel):
    """Schema for marking notification as read"""
    is_read: bool = True


class NotificationStats(BaseModel):
    """Schema for notification statistics"""
    total: int
    unread_count: int
    by_type: dict
    by_severity: dict