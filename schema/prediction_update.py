from pydantic import BaseModel
from typing import Optional

class PredictionUpdate(BaseModel):
    predicted_category: Optional[str] = None
    confidence: Optional[float] = None
