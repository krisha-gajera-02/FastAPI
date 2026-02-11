from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PredictionDB(BaseModel):
    id: int
    predicted_category: str
    confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
