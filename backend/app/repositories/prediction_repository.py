from typing import Optional, List
from supabase import Client
from app.models.prediction import Prediction
from app.core.exceptions import NotFoundException
import json


class PredictionRepository:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "predictions"
    
    def _parse_forecast(self, forecast_data):
        """
        Parse forecast field - handles both string and dict
        Compatible avec anciennes données (string) et nouvelles (dict)
        """
        if isinstance(forecast_data, str):
            try:
                return json.loads(forecast_data)
            except (json.JSONDecodeError, TypeError):
                return forecast_data
        elif isinstance(forecast_data, dict):
            return forecast_data
        else:
            return forecast_data
    
    async def create_prediction(
        self,
        server_id: str,
        forecast: dict
    ) -> Prediction:
        """Create a new prediction record"""
        # ✅ Envoyer directement le dict - Supabase/PostgreSQL gère JSONB
        response = self.supabase.table(self.table).insert({
            "server_id": server_id,
            "forecast": forecast  # ← PAS de json.dumps() !
        }).execute()
        
        if not response.data:
            raise Exception("Failed to create prediction")
        
        prediction_data = response.data[0]
        # ✅ Parse au cas où (rétrocompatibilité)
        prediction_data["forecast"] = self._parse_forecast(prediction_data["forecast"])
        
        return Prediction(**prediction_data)
    
    async def get_prediction_by_id(self, prediction_id: str) -> Optional[Prediction]:
        """Get specific prediction by ID"""
        response = self.supabase.table(self.table).select("*").eq("id", prediction_id).execute()
        
        if not response.data:
            return None
        
        prediction_data = response.data[0]
        # ✅ Parse avec helper (gère string et dict)
        prediction_data["forecast"] = self._parse_forecast(prediction_data["forecast"])
        
        return Prediction(**prediction_data)
    
    async def get_latest_prediction(self, server_id: str) -> Optional[Prediction]:
        """Get the most recent prediction for a server"""
        response = self.supabase.table(self.table).select("*").eq(
            "server_id", server_id
        ).order("created_at", desc=True).limit(1).execute()
        
        if not response.data:
            return None
        
        prediction_data = response.data[0]
        # ✅ Parse avec helper
        prediction_data["forecast"] = self._parse_forecast(prediction_data["forecast"])
        
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
            # ✅ Parse avec helper
            pred_data["forecast"] = self._parse_forecast(pred_data["forecast"])
            predictions.append(Prediction(**pred_data))
        
        return predictions
    
    async def get_prediction_count(self, server_id: str) -> int:
        """Get total number of predictions for a server"""
        response = self.supabase.table(self.table).select(
            "id", count="exact"
        ).eq("server_id", server_id).execute()
        
        return response.count if response.count else 0