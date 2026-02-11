from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime
from datetime import datetime
from db.base import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    age = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    income_lpa = Column(Float)
    smoker = Column(Boolean)
    city = Column(String)
    occupation = Column(String)

    bmi = Column(Float)
    age_group = Column(String)
    lifestyle_risk = Column(String)
    city_tier = Column(Integer)

    predicted_category = Column(String)
    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
