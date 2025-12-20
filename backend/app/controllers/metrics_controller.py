from fastapi import APIRouter, Depends
from supabase import Client
from app.schemas.metrics import MetricsIngest, MetricsResponse
from app.services.metrics_service import MetricsService
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.server_repository import ServerRepository
from app.database.supabase import get_supabase

router = APIRouter()


def get_metrics_service(supabase: Client = Depends(get_supabase)) -> MetricsService:
    """Dependency to get MetricsService instance"""
    metrics_repo = MetricsRepository(supabase)
    server_repo = ServerRepository(supabase)
    return MetricsService(metrics_repo, server_repo)


@router.post("/ingest", response_model=MetricsResponse, status_code=201)
async def ingest_metrics(
    metrics_data: MetricsIngest,
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """
    **Agent endpoint to send metrics**
    
    Authentication: Uses server API key (not JWT token)
    
    Send metrics data:
    - **api_key**: Server API key (get from POST /api/servers)
    - **cpu_percent**: CPU usage (0-100)
    - **ram_percent**: RAM usage (0-100)
    - **disk_read**: Disk read bytes
    - **disk_write**: Disk write bytes
    - **net_sent**: Network sent bytes
    - **net_recv**: Network received bytes
    
    This endpoint is called by the monitoring agent every 30 seconds
    """
    return await metrics_service.ingest_metrics(metrics_data)