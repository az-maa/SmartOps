from app.repositories.anomaly_repository import AnomalyRepository
from app.repositories.server_repository import ServerRepository
from app.schemas.anomaly import (
    AnomalyCreate,
    AnomalyResponse,
    AnomalyListResponse,
    AnomalyStats
)
from app.core.exceptions import NotFoundException, ForbiddenException
from datetime import datetime
from typing import Optional


class AnomalyService:
    def __init__(self, anomaly_repo: AnomalyRepository, server_repo: ServerRepository):
        self.anomaly_repo = anomaly_repo
        self.server_repo = server_repo
    
    async def create_anomaly(self, anomaly_data: AnomalyCreate) -> AnomalyResponse:
        """
        Create anomaly (called by AI service)
        In production, this should require special AI service authentication
        """
        # Verify server exists
        server = await self.server_repo.get_server_by_id(anomaly_data.server_id)
        if not server:
            raise NotFoundException(detail="Server not found")
        
        # Create anomaly
        anomaly = await self.anomaly_repo.create_anomaly(
            server_id=anomaly_data.server_id,
            timestamp=anomaly_data.timestamp,
            type=anomaly_data.type,
            severity=anomaly_data.severity,
            explanation=anomaly_data.explanation,
            metrics=anomaly_data.metrics
        )
        
        return AnomalyResponse.model_validate(anomaly)
    
    async def get_server_anomalies(
        self,
        server_id: str,
        user_id: str,
        severity: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> AnomalyListResponse:
        """Get anomalies for a server (with authorization)"""
        # Check authorization
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Get anomalies
        anomalies = await self.anomaly_repo.get_anomalies_by_server(
            server_id=server_id,
            severity=severity,
            from_time=from_time,
            to_time=to_time,
            limit=limit,
            offset=offset
        )
        
        total = await self.anomaly_repo.get_anomaly_count(
            server_id=server_id,
            severity=severity,
            from_time=from_time,
            to_time=to_time
        )
        
        return AnomalyListResponse(
            anomalies=[AnomalyResponse.model_validate(a) for a in anomalies],
            total=total,
            server_id=server_id
        )
    
    async def get_anomaly(
        self,
        anomaly_id: str,
        user_id: str
    ) -> AnomalyResponse:
        """Get specific anomaly (with authorization)"""
        anomaly = await self.anomaly_repo.get_anomaly_by_id(anomaly_id)
        
        if not anomaly:
            raise NotFoundException(detail="Anomaly not found")
        
        # Check if user owns the server
        server = await self.server_repo.get_server_by_id(str(anomaly.server_id))
        
        if not server or str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this anomaly")
        
        return AnomalyResponse.model_validate(anomaly)
    
    async def get_anomaly_stats(
        self,
        server_id: str,
        user_id: str,
        days: int = 7
    ) -> AnomalyStats:
        """Get anomaly statistics for a server"""
        # Check authorization
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Get stats
        stats = await self.anomaly_repo.get_anomaly_stats(server_id, days)
        
        return AnomalyStats(**stats)