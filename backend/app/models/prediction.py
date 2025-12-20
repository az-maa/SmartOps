from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class Prediction(BaseModel):
    """Domain model for Prediction"""
    id: UUID
    server_id: UUID
    forecast: dict  # JSON data containing prediction results
    created_at: datetime
    
    class Config:
        from_attributes = True