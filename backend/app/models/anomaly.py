from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class Anomaly(BaseModel):
    """Domain model for Anomaly"""
    id: UUID
    server_id: UUID
    timestamp: datetime
    type: str
    severity: str
    explanation: str
    metrics: dict  # JSON data of metrics at time of anomaly
    created_at: datetime
    
    class Config:
        from_attributes = True