from fastapi import FastAPI, Depends,HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from schema.user_input import UserInput,UpdateFieldRequest
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
    
@app.get("/predictions")
def get_all_predictions(db: Session = Depends(get_db)):
    records = db.query(Prediction).order_by(Prediction.created_at.desc()).all()
    return records

@app.get("/predictions/{prediction_id}")
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    record = db.query(Prediction).filter(Prediction.id == prediction_id).first()

    if not record:
        return JSONResponse(status_code=404, content="Prediction not found")

    return record

from schema.prediction_update import PredictionUpdate

@app.put("/prediction/{id}")
def update_prediction(
    id: int,
    update: UpdateFieldRequest,
    db: Session = Depends(get_db)
):
    record = db.query(Prediction).filter(Prediction.id == id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # check field exists in model
    if not hasattr(record, update.field_name):
        raise HTTPException(status_code=400, detail="Invalid field name")

    # dynamic update
    setattr(record, update.field_name, update.new_value)

    db.commit()
    db.refresh(record)

    return {
        "message": "Field updated successfully",
        "updated_field": update.field_name,
        "new_value": update.new_value
    }

@app.delete("/predictions/{prediction_id}")
def delete_prediction(prediction_id: int, db: Session = Depends(get_db)):
    record = db.query(Prediction).filter(Prediction.id == prediction_id).first()

    if not record:
        return JSONResponse(status_code=404, content="Prediction not found")

    db.delete(record)
    db.commit()

    return {"message": "Prediction deleted successfully"}

