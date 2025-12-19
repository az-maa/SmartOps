from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class ServerCreate(BaseModel):
    """Schema for creating a new server"""
    name: str = Field(..., min_length=1, max_length=100)
    ip: str = Field(..., min_length=7, max_length=45)


class ServerUpdate(BaseModel):
    """Schema for updating server"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    ip: Optional[str] = Field(None, min_length=7, max_length=45)
    status: Optional[str] = Field(None, pattern="^(online|offline|warning)$")


class ServerResponse(BaseModel):
    """Schema for server in responses"""
    id: UUID
    user_id: UUID
    name: str
    ip: str
    status: str
    api_key: Optional[str] = None
    created_at: datetime
    last_seen: datetime
    
    class Config:
        from_attributes = True


class ServerListResponse(BaseModel):
    """Schema for list of servers"""
    servers: list[ServerResponse]
    total: int