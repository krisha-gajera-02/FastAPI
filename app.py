from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from schema.user_input import UserInput
from schema.prediction_response import PredictionResponse
from model.predict import predict_output, model, MODEL_VERSION

from db.session import get_db
from db.models import Prediction
from db.base import Base
from config.database import engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Insurance Premium Prediction API")

@app.get('/')
def home():
    return {"message": "Insurance premium prediction API"}

@app.get('/health')
def health_check():
    return {
        "status": "OK",
        "version": MODEL_VERSION,
        "model_loaded": model is not None
    }

@app.post('/predict', response_model=PredictionResponse)
def predict_premium(
    data: UserInput,
    db: Session = Depends(get_db)
):
    user_input = {
        "bmi": data.bmi,
        "age_group": data.age_group,
        "lifestyle_risk": data.lifestyle_risk,
        "city_tier": data.city_tier,
        "income_lpa": data.income_lpa,
        "occupation": data.occupation
    }

    try:
        result = predict_output(user_input)

        db_entry = Prediction(
            age=data.age,
            weight=data.weight,
            height=data.height,
            income_lpa=data.income_lpa,
            smoker=data.smoker,
            city=data.city,
            occupation=data.occupation,

            bmi=data.bmi,
            age_group=data.age_group,
            lifestyle_risk=data.lifestyle_risk,
            city_tier=data.city_tier,

            predicted_category=result["predicted_category"],
            confidence=result.get("confidence")
        )

        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)

        return JSONResponse(
            status_code=200,
            content=result
        )

    except Exception as e:
        return JSONResponse(status_code=500, content=str(e))
