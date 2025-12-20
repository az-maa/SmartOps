from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class AnomalyCreate(BaseModel):
    """Schema for AI service to create anomaly"""
    server_id: str = Field(..., description="Server ID where anomaly was detected")
    timestamp: datetime = Field(..., description="When the anomaly occurred")
    type: str = Field(..., description="Type of anomaly (e.g., cpu_spike, memory_leak)")
    severity: str = Field(..., pattern="^(low|medium|high|critical)$", description="Severity level")
    explanation: str = Field(..., min_length=1, description="AI explanation of the anomaly")
    metrics: dict = Field(..., description="Metrics data at time of anomaly")


class AnomalyResponse(BaseModel):
    """Schema for anomaly in responses"""
    id: UUID
    server_id: UUID
    timestamp: datetime
    type: str
    severity: str
    explanation: str
    metrics: dict
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnomalyListResponse(BaseModel):
    """Schema for paginated list of anomalies"""
    anomalies: list[AnomalyResponse]
    total: int
    server_id: UUID


class AnomalyStats(BaseModel):
    """Schema for anomaly statistics"""
    server_id: UUID
    total_anomalies: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    most_recent: Optional[datetime] = None