from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ForecastPoint(BaseModel):
    timestamp: datetime
    value: float

class PredictionCreate(BaseModel):
    server_id: str
    forecast: List[ForecastPoint]

class PredictionResponse(BaseModel):
    id: str
    server_id: str
    forecast: List[dict]  # JSONB from DB
    created_at: datetime