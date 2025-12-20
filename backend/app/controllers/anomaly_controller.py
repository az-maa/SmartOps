from fastapi import APIRouter, Depends
from supabase import Client
from app.schemas.anomaly import AnomalyCreate, AnomalyResponse
from app.services.anomaly_service import AnomalyService
from app.repositories.anomaly_repository import AnomalyRepository
from app.repositories.server_repository import ServerRepository
from app.database.supabase import get_supabase
from app.repositories.notification_repository import NotificationRepository

router = APIRouter()


def get_anomaly_service(supabase: Client = Depends(get_supabase)) -> AnomalyService:
    """Dependency to get AnomalyService instance"""
    anomaly_repo = AnomalyRepository(supabase)
    server_repo = ServerRepository(supabase)
    notification_repo = NotificationRepository(supabase)  # ADD THIS
    return AnomalyService(anomaly_repo, server_repo, notification_repo)  # ADD notification_repo


@router.post("", response_model=AnomalyResponse, status_code=201)
async def create_anomaly(
    anomaly_data: AnomalyCreate,
    anomaly_service: AnomalyService = Depends(get_anomaly_service)
):
    """
    **Create anomaly (AI Service endpoint)**
    
    This endpoint is called by the AI service when it detects an anomaly.
    
    Send:
    - **server_id**: Server where anomaly was detected
    - **timestamp**: When it occurred
    - **type**: Type of anomaly (cpu_spike, memory_leak, etc.)
    - **severity**: low/medium/high/critical
    - **explanation**: AI-generated explanation
    - **metrics**: Metrics data at time of anomaly
    
    ⚠️ In production, this should require AI service authentication token
    """
    return await anomaly_service.create_anomaly(anomaly_data)