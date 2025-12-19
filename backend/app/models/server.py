from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class Server(BaseModel):
    """Domain model for Server"""
    id: UUID
    user_id: UUID
    name: str
    ip: str
    status: str = "online"
    api_key: Optional[str] = None
    created_at: datetime
    last_seen: datetime
    
    class Config:
        from_attributes = True