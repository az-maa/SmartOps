from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class PredictionCreate(BaseModel):
    """Schema for AI service to create prediction"""
    server_id: str = Field(..., description="Server ID for prediction")
    forecast: dict = Field(..., description="Forecast data from ML model")


class PredictionResponse(BaseModel):
    """Schema for prediction in responses"""
    id: UUID
    server_id: UUID
    forecast: dict
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    """Schema for list of predictions"""
    predictions: list[PredictionResponse]
    total: int
    server_id: UUID