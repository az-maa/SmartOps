from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class Metrics(BaseModel):
    """Domain model for Metrics"""
    id: UUID
    server_id: UUID
    timestamp: datetime
    cpu_percent: float
    ram_percent: float
    disk_read: int
    disk_write: int
    net_sent: int
    net_recv: int
    created_at: datetime
    
    class Config:
        from_attributes = True