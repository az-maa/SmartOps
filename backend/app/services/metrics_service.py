from app.repositories.metrics_repository import MetricsRepository
from app.repositories.server_repository import ServerRepository
from app.schemas.metrics import (
    MetricsIngest,
    MetricsResponse,
    MetricsListResponse,
    MetricsSummary
)
from app.core.exceptions import UnauthorizedException, NotFoundException, ForbiddenException
from datetime import datetime
from typing import Optional


class MetricsService:
    def __init__(self, metrics_repo: MetricsRepository, server_repo: ServerRepository):
        self.metrics_repo = metrics_repo
        self.server_repo = server_repo
    
    async def ingest_metrics(self, metrics_data: MetricsIngest) -> MetricsResponse:
        """
        Ingest metrics from monitoring agent
        Authenticates using server API key
        """
        # Verify API key and get server
        server = await self.server_repo.get_server_by_api_key(metrics_data.api_key)
        
        if not server:
            raise UnauthorizedException(detail="Invalid API key")
        
        # Insert metrics
        metrics = await self.metrics_repo.insert_metrics(
            server_id=str(server.id),
            cpu_percent=metrics_data.cpu_percent,
            ram_percent=metrics_data.ram_percent,
            disk_read=metrics_data.disk_read,
            disk_write=metrics_data.disk_write,
            net_sent=metrics_data.net_sent,
            net_recv=metrics_data.net_recv
        )
        
        # Update server's last_seen timestamp
        await self.server_repo.update_last_seen(str(server.id))
        
        return MetricsResponse.model_validate(metrics)
    
    async def get_server_metrics(
        self,
        server_id: str,
        user_id: str,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> MetricsListResponse:
        """Get metrics for a server (with authorization check)"""
        # Check if server exists and user owns it
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Get metrics
        metrics = await self.metrics_repo.get_metrics_by_server(
            server_id=server_id,
            from_time=from_time,
            to_time=to_time,
            limit=limit,
            offset=offset
        )
        
        total = await self.metrics_repo.get_metrics_count(
            server_id=server_id,
            from_time=from_time,
            to_time=to_time
        )
        
        return MetricsListResponse(
            metrics=[MetricsResponse.model_validate(m) for m in metrics],
            total=total,
            server_id=server_id
        )
    
    async def get_latest_metrics(
        self,
        server_id: str,
        user_id: str
    ) -> Optional[MetricsResponse]:
        """Get latest metrics for a server"""
        # Check authorization
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Get latest metrics
        metrics = await self.metrics_repo.get_latest_metrics(server_id)
        
        if not metrics:
            return None
        
        return MetricsResponse.model_validate(metrics)
    
    async def get_metrics_summary(
        self,
        server_id: str,
        user_id: str,
        hours: int = 24
    ) -> Optional[MetricsSummary]:
        """Get aggregated metrics summary"""
        # Check authorization
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Get summary
        summary = await self.metrics_repo.get_metrics_summary(server_id, hours)
        
        if not summary:
            return None
        
        return MetricsSummary(**summary)