from fastapi import APIRouter, Depends
from supabase import Client
from app.schemas.prediction import PredictionCreate, PredictionResponse
from app.services.prediction_service import PredictionService
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.server_repository import ServerRepository
from app.database.supabase import get_supabase

router = APIRouter()


def get_prediction_service(supabase: Client = Depends(get_supabase)) -> PredictionService:
    """Dependency to get PredictionService instance"""
    prediction_repo = PredictionRepository(supabase)
    server_repo = ServerRepository(supabase)
    return PredictionService(prediction_repo, server_repo)


@router.post("", response_model=PredictionResponse, status_code=201)
async def create_prediction(
    prediction_data: PredictionCreate,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    **Create prediction (AI Service endpoint)**
    
    This endpoint is called by the AI service to store forecast results.
    
    Send:
    - **server_id**: Server for prediction
    - **forecast**: Forecast data from ML model (JSON)
    
    ⚠️ In production, this should require AI service authentication token
    """
    return await prediction_service.create_prediction(prediction_data)