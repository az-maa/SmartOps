from typing import Optional, List
from supabase import Client
from app.models.prediction import Prediction
from app.core.exceptions import NotFoundException
import json


class PredictionRepository:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "predictions"
    
    async def create_prediction(
        self,
        server_id: str,
        forecast: dict
    ) -> Prediction:
        """Create a new prediction record"""
        response = self.supabase.table(self.table).insert({
            "server_id": server_id,
            "forecast": json.dumps(forecast)
        }).execute()
        
        if not response.data:
            raise Exception("Failed to create prediction")
        
        prediction_data = response.data[0]
        prediction_data["forecast"] = json.loads(prediction_data["forecast"])
        
        return Prediction(**prediction_data)
    
    async def get_prediction_by_id(self, prediction_id: str) -> Optional[Prediction]:
        """Get specific prediction by ID"""
        response = self.supabase.table(self.table).select("*").eq("id", prediction_id).execute()
        
        if not response.data:
            return None
        
        prediction_data = response.data[0]
        prediction_data["forecast"] = json.loads(prediction_data["forecast"])
        
        return Prediction(**prediction_data)
    
    async def get_latest_prediction(self, server_id: str) -> Optional[Prediction]:
        """Get the most recent prediction for a server"""
        response = self.supabase.table(self.table).select("*").eq(
            "server_id", server_id
        ).order("created_at", desc=True).limit(1).execute()
        
        if not response.data:
            return None
        
        prediction_data = response.data[0]
        prediction_data["forecast"] = json.loads(prediction_data["forecast"])
        
        return Prediction(**prediction_data)
    
    async def get_predictions_by_server(
        self,
        server_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Prediction]:
        """Get prediction history for a server"""
        response = self.supabase.table(self.table).select("*").eq(
            "server_id", server_id
        ).order("created_at", desc=True).range(
            offset, offset + limit - 1
        ).execute()
        
        if not response.data:
            return []
        
        predictions = []
        for pred_data in response.data:
            pred_data["forecast"] = json.loads(pred_data["forecast"])
            predictions.append(Prediction(**pred_data))
        
        return predictions
    
    async def get_prediction_count(self, server_id: str) -> int:
        """Get total number of predictions for a server"""
        response = self.supabase.table(self.table).select(
            "id", count="exact"
        ).eq("server_id", server_id).execute()
        
        return response.count if response.count else 0