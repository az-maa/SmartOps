from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class MetricsIngest(BaseModel):
    """Schema for agent to send metrics (uses API key, not user auth)"""
    api_key: str = Field(..., description="Server API key for authentication")
    cpu_percent: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    ram_percent: float = Field(..., ge=0, le=100, description="RAM usage percentage")
    disk_read: int = Field(..., ge=0, description="Disk read bytes")
    disk_write: int = Field(..., ge=0, description="Disk write bytes")
    net_sent: int = Field(..., ge=0, description="Network sent bytes")
    net_recv: int = Field(..., ge=0, description="Network received bytes")


class MetricsResponse(BaseModel):
    """Schema for metrics in responses"""
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


class MetricsListResponse(BaseModel):
    """Schema for paginated list of metrics"""
    metrics: list[MetricsResponse]
    total: int
    server_id: UUID


class MetricsSummary(BaseModel):
    """Schema for aggregated metrics summary"""
    server_id: UUID
    avg_cpu: float
    avg_ram: float
    max_cpu: float
    max_ram: float
    total_disk_read: int
    total_disk_write: int
    total_net_sent: int
    total_net_recv: int
    period_start: datetime
    period_end: datetime