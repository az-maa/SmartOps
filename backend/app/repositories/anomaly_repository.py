from typing import Optional, List
from supabase import Client
from app.models.anomaly import Anomaly
from app.core.exceptions import NotFoundException
from datetime import datetime, timedelta
import json


class AnomalyRepository:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "anomalies"
    
    async def create_anomaly(
        self,
        server_id: str,
        timestamp: datetime,
        type: str,
        severity: str,
        explanation: str,
        metrics: dict
    ) -> Anomaly:
        """Create a new anomaly record"""
        response = self.supabase.table(self.table).insert({
            "server_id": server_id,
            "timestamp": timestamp.isoformat(),
            "type": type,
            "severity": severity,
            "explanation": explanation,
            "metrics": json.dumps(metrics)
        }).execute()
        
        if not response.data:
            raise Exception("Failed to create anomaly")
        
        # Parse JSON back to dict
        anomaly_data = response.data[0]
        anomaly_data["metrics"] = json.loads(anomaly_data["metrics"])
        
        return Anomaly(**anomaly_data)
    
    async def get_anomaly_by_id(self, anomaly_id: str) -> Optional[Anomaly]:
        """Get specific anomaly by ID"""
        response = self.supabase.table(self.table).select("*").eq("id", anomaly_id).execute()
        
        if not response.data:
            return None
        
        anomaly_data = response.data[0]
        anomaly_data["metrics"] = json.loads(anomaly_data["metrics"])
        
        return Anomaly(**anomaly_data)
    
    async def get_anomalies_by_server(
        self,
        server_id: str,
        severity: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Anomaly]:
        """Get anomalies for a server with filters"""
        query = self.supabase.table(self.table).select("*").eq("server_id", server_id)
        
        # Apply filters
        if severity:
            query = query.eq("severity", severity)
        if from_time:
            query = query.gte("timestamp", from_time.isoformat())
        if to_time:
            query = query.lte("timestamp", to_time.isoformat())
        
        # Order and paginate
        response = query.order("timestamp", desc=True).range(
            offset, offset + limit - 1
        ).execute()
        
        if not response.data:
            return []
        
        anomalies = []
        for anomaly_data in response.data:
            anomaly_data["metrics"] = json.loads(anomaly_data["metrics"])
            anomalies.append(Anomaly(**anomaly_data))
        
        return anomalies
    
    async def get_anomaly_count(
        self,
        server_id: str,
        severity: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None
    ) -> int:
        """Get total count of anomalies"""
        query = self.supabase.table(self.table).select("id", count="exact").eq("server_id", server_id)
        
        if severity:
            query = query.eq("severity", severity)
        if from_time:
            query = query.gte("timestamp", from_time.isoformat())
        if to_time:
            query = query.lte("timestamp", to_time.isoformat())
        
        response = query.execute()
        return response.count if response.count else 0
    
    async def get_anomaly_stats(self, server_id: str, days: int = 7) -> dict:
        """Get anomaly statistics for a server"""
        from_time = datetime.utcnow() - timedelta(days=days)
        
        # Get all anomalies in time range
        anomalies = await self.get_anomalies_by_server(
            server_id=server_id,
            from_time=from_time,
            limit=10000
        )
        
        if not anomalies:
            return {
                "server_id": server_id,
                "total_anomalies": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "most_recent": None
            }
        
        # Calculate stats
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for anomaly in anomalies:
            if anomaly.severity in severity_counts:
                severity_counts[anomaly.severity] += 1
        
        return {
            "server_id": server_id,
            "total_anomalies": len(anomalies),
            "critical_count": severity_counts["critical"],
            "high_count": severity_counts["high"],
            "medium_count": severity_counts["medium"],
            "low_count": severity_counts["low"],
            "most_recent": anomalies[0].timestamp if anomalies else None
        }