from typing import Optional, List
from supabase import Client
from app.models.metrics import Metrics
from app.core.exceptions import NotFoundException
from datetime import datetime, timedelta


class MetricsRepository:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "metrics"
    
    async def insert_metrics(
        self,
        server_id: str,
        cpu_percent: float,
        ram_percent: float,
        disk_read: int,
        disk_write: int,
        net_sent: int,
        net_recv: int
    ) -> Metrics:
        """Insert new metrics data"""
        response = self.supabase.table(self.table).insert({
            "server_id": server_id,
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": cpu_percent,
            "ram_percent": ram_percent,
            "disk_read": disk_read,
            "disk_write": disk_write,
            "net_sent": net_sent,
            "net_recv": net_recv
        }).execute()
        
        if not response.data:
            raise Exception("Failed to insert metrics")
        
        return Metrics(**response.data[0])
    
    async def get_metrics_by_server(
        self,
        server_id: str,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Metrics]:
        """Get metrics for a server with optional time range"""
        query = self.supabase.table(self.table).select("*").eq("server_id", server_id)
        
        # Apply time filters if provided
        if from_time:
            query = query.gte("timestamp", from_time.isoformat())
        if to_time:
            query = query.lte("timestamp", to_time.isoformat())
        
        # Order by timestamp descending and apply pagination
        response = query.order("timestamp", desc=True).range(
            offset, offset + limit - 1
        ).execute()
        
        if not response.data:
            return []
        
        return [Metrics(**metric_data) for metric_data in response.data]
    
    async def get_latest_metrics(self, server_id: str) -> Optional[Metrics]:
        """Get the most recent metrics for a server"""
        response = self.supabase.table(self.table).select("*").eq(
            "server_id", server_id
        ).order("timestamp", desc=True).limit(1).execute()
        
        if not response.data:
            return None
        
        return Metrics(**response.data[0])
    
    async def get_metrics_count(
        self,
        server_id: str,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None
    ) -> int:
        """Get total count of metrics for a server"""
        query = self.supabase.table(self.table).select("id", count="exact").eq("server_id", server_id)
        
        if from_time:
            query = query.gte("timestamp", from_time.isoformat())
        if to_time:
            query = query.lte("timestamp", to_time.isoformat())
        
        response = query.execute()
        return response.count if response.count else 0
    
    async def get_metrics_summary(
        self,
        server_id: str,
        hours: int = 24
    ) -> dict:
        """Get aggregated metrics summary for the last N hours"""
        from_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get all metrics in the time range
        metrics = await self.get_metrics_by_server(
            server_id=server_id,
            from_time=from_time,
            limit=10000  # Get all for aggregation
        )
        
        if not metrics:
            return None
        
        # Calculate aggregates
        cpu_values = [m.cpu_percent for m in metrics]
        ram_values = [m.ram_percent for m in metrics]
        
        return {
            "server_id": server_id,
            "avg_cpu": sum(cpu_values) / len(cpu_values),
            "avg_ram": sum(ram_values) / len(ram_values),
            "max_cpu": max(cpu_values),
            "max_ram": max(ram_values),
            "total_disk_read": sum(m.disk_read for m in metrics),
            "total_disk_write": sum(m.disk_write for m in metrics),
            "total_net_sent": sum(m.net_sent for m in metrics),
            "total_net_recv": sum(m.net_recv for m in metrics),
            "period_start": from_time,
            "period_end": datetime.utcnow()
        }