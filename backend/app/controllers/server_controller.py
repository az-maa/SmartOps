from fastapi import APIRouter, Depends, Query
from supabase import Client
from app.schemas.server import ServerCreate, ServerUpdate, ServerResponse, ServerListResponse
from app.services.server_service import ServerService
from app.repositories.server_repository import ServerRepository
from app.database.supabase import get_supabase
from app.core.dependencies import get_current_user_id
from app.schemas.metrics import MetricsListResponse, MetricsResponse, MetricsSummary
from app.services.metrics_service import MetricsService
from app.repositories.metrics_repository import MetricsRepository
from datetime import datetime
from typing import Optional
from app.schemas.anomaly import AnomalyListResponse, AnomalyStats
from app.schemas.prediction import PredictionResponse, PredictionListResponse
from app.services.anomaly_service import AnomalyService
from app.services.prediction_service import PredictionService
from app.repositories.anomaly_repository import AnomalyRepository
from app.repositories.prediction_repository import PredictionRepository

router = APIRouter()


def get_server_service(supabase: Client = Depends(get_supabase)) -> ServerService:
    """Dependency to get ServerService instance"""
    server_repo = ServerRepository(supabase)
    return ServerService(server_repo)
def get_metrics_service(supabase: Client = Depends(get_supabase)) -> MetricsService:
    """Dependency to get MetricsService instance"""
    metrics_repo = MetricsRepository(supabase)
    server_repo = ServerRepository(supabase)
    return MetricsService(metrics_repo, server_repo)
def get_anomaly_service(supabase: Client = Depends(get_supabase)) -> AnomalyService:
    """Dependency to get AnomalyService instance"""
    anomaly_repo = AnomalyRepository(supabase)
    server_repo = ServerRepository(supabase)
    return AnomalyService(anomaly_repo, server_repo)


def get_prediction_service(supabase: Client = Depends(get_supabase)) -> PredictionService:
    """Dependency to get PredictionService instance"""
    prediction_repo = PredictionRepository(supabase)
    server_repo = ServerRepository(supabase)
    return PredictionService(prediction_repo, server_repo)


@router.post("", response_model=ServerResponse, status_code=201)
async def create_server(
    server_data: ServerCreate,
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Create a new server**
    
    - **name**: Server name (1-100 characters)
    - **ip**: Server IP address (IPv4 or IPv6)
    
    Returns server info with generated API key for agent authentication
    
    Requires authentication token
    """
    return await server_service.create_server(user_id, server_data)


@router.get("", response_model=ServerListResponse)
async def get_my_servers(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Get all your servers**
    
    Returns paginated list of all servers owned by current user
    
    Requires authentication token
    """
    return await server_service.get_user_servers(user_id, limit, offset)


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(
    server_id: str,
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Get specific server by ID**
    
    Returns server details (only if you own it)
    
    Requires authentication token
    """
    return await server_service.get_server(server_id, user_id)


@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: str,
    update_data: ServerUpdate,
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Update server information**
    
    All fields are optional:
    - **name**: Updated server name
    - **ip**: Updated IP address
    - **status**: Updated status (online/offline/warning)
    
    Requires authentication token
    """
    return await server_service.update_server(server_id, user_id, update_data)


@router.delete("/{server_id}")
async def delete_server(
    server_id: str,
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Delete server (PERMANENT)**
    
    This will also delete all associated metrics, anomalies, and predictions
    
    Requires authentication token
    """
    await server_service.delete_server(server_id, user_id)
    return {"message": "Server deleted successfully"}
# ==================== SERVER METRICS ====================

@router.get("/{server_id}/metrics", response_model=MetricsListResponse)
async def get_server_metrics(
    server_id: str,
    from_time: Optional[datetime] = Query(None, description="Start time filter"),
    to_time: Optional[datetime] = Query(None, description="End time filter"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """
    **Get metrics for a server**
    
    Optional filters:
    - **from_time**: Start time (ISO format)
    - **to_time**: End time (ISO format)
    - **limit**: Number of results
    - **offset**: Pagination offset
    
    Requires authentication token
    """
    return await metrics_service.get_server_metrics(
        server_id=server_id,
        user_id=user_id,
        from_time=from_time,
        to_time=to_time,
        limit=limit,
        offset=offset
    )


@router.get("/{server_id}/metrics/latest", response_model=MetricsResponse)
async def get_latest_metrics(
    server_id: str,
    user_id: str = Depends(get_current_user_id),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """
    **Get latest metrics snapshot for a server**
    
    Returns the most recent metrics data point
    
    Requires authentication token
    """
    return await metrics_service.get_latest_metrics(server_id, user_id)


@router.get("/{server_id}/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    server_id: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    user_id: str = Depends(get_current_user_id),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """
    **Get aggregated metrics summary**
    
    Returns averages, max values, and totals for the specified time period
    
    - **hours**: Number of hours to look back (default: 24, max: 168/1 week)
    
    Requires authentication token
    """
    return await metrics_service.get_metrics_summary(server_id, user_id, hours)
# ==================== SERVER ANOMALIES ====================

@router.get("/{server_id}/anomalies", response_model=AnomalyListResponse)
async def get_server_anomalies(
    server_id: str,
    severity: Optional[str] = Query(None, pattern="^(low|medium|high|critical)$"),
    from_time: Optional[datetime] = Query(None),
    to_time: Optional[datetime] = Query(None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
    anomaly_service: AnomalyService = Depends(get_anomaly_service)
):
    """
    **Get anomalies detected for a server**
    
    Optional filters:
    - **severity**: Filter by severity (low/medium/high/critical)
    - **from_time**: Start time
    - **to_time**: End time
    
    Requires authentication token
    """
    return await anomaly_service.get_server_anomalies(
        server_id=server_id,
        user_id=user_id,
        severity=severity,
        from_time=from_time,
        to_time=to_time,
        limit=limit,
        offset=offset
    )


@router.get("/{server_id}/anomalies/stats", response_model=AnomalyStats)
async def get_anomaly_stats(
    server_id: str,
    days: int = Query(default=7, ge=1, le=30),
    user_id: str = Depends(get_current_user_id),
    anomaly_service: AnomalyService = Depends(get_anomaly_service)
):
    """
    **Get anomaly statistics for a server**
    
    Returns counts by severity and most recent anomaly
    
    - **days**: Number of days to look back (default: 7, max: 30)
    
    Requires authentication token
    """
    return await anomaly_service.get_anomaly_stats(server_id, user_id, days)


# ==================== SERVER PREDICTIONS ====================

@router.get("/{server_id}/predictions/latest", response_model=PredictionResponse)
async def get_latest_prediction(
    server_id: str,
    user_id: str = Depends(get_current_user_id),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    **Get latest prediction for a server**
    
    Returns the most recent forecast generated by AI
    
    Requires authentication token
    """
    return await prediction_service.get_latest_prediction(server_id, user_id)


@router.get("/{server_id}/predictions", response_model=PredictionListResponse)
async def get_prediction_history(
    server_id: str,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    **Get prediction history for a server**
    
    Returns past predictions with pagination
    
    Requires authentication token
    """
    return await prediction_service.get_prediction_history(
        server_id=server_id,
        user_id=user_id,
        limit=limit,
        offset=offset
    )