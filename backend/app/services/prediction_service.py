from app.repositories.prediction_repository import PredictionRepository
from app.repositories.server_repository import ServerRepository
from app.schemas.prediction import (
    PredictionCreate,
    PredictionResponse,
    PredictionListResponse
)
from app.core.exceptions import NotFoundException, ForbiddenException
from typing import Optional


class PredictionService:
    def __init__(self, prediction_repo: PredictionRepository, server_repo: ServerRepository):
        self.prediction_repo = prediction_repo
        self.server_repo = server_repo
    
    async def create_prediction(self, prediction_data: PredictionCreate) -> PredictionResponse:
        """
        Create prediction (called by AI service)
        In production, this should require special AI service authentication
        """
        # Verify server exists
        server = await self.server_repo.get_server_by_id(prediction_data.server_id)
        if not server:
            raise NotFoundException(detail="Server not found")
        
        # Create prediction
        prediction = await self.prediction_repo.create_prediction(
            server_id=prediction_data.server_id,
            forecast=prediction_data.forecast
        )
        
        return PredictionResponse.model_validate(prediction)
    
    async def get_latest_prediction(
        self,
        server_id: str,
        user_id: str
    ) -> Optional[PredictionResponse]:
        """Get latest prediction for a server"""
        # Check authorization
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Get latest prediction
        prediction = await self.prediction_repo.get_latest_prediction(server_id)
        
        if not prediction:
            return None
        
        return PredictionResponse.model_validate(prediction)
    
    async def get_prediction_history(
        self,
        server_id: str,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> PredictionListResponse:
        """Get prediction history for a server"""
        # Check authorization
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Get predictions
        predictions = await self.prediction_repo.get_predictions_by_server(
            server_id=server_id,
            limit=limit,
            offset=offset
        )
        
        total = await self.prediction_repo.get_prediction_count(server_id)
        
        return PredictionListResponse(
            predictions=[PredictionResponse.model_validate(p) for p in predictions],
            total=total,
            server_id=server_id
        )
    
    async def get_prediction(
        self,
        prediction_id: str,
        user_id: str
    ) -> PredictionResponse:
        """Get specific prediction by ID"""
        prediction = await self.prediction_repo.get_prediction_by_id(prediction_id)
        
        if not prediction:
            raise NotFoundException(detail="Prediction not found")
        
        # Check authorization
        server = await self.server_repo.get_server_by_id(str(prediction.server_id))
        
        if not server or str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this prediction")
        
        return PredictionResponse.model_validate(prediction)