import pickle
import pandas as pd

# Load trained model
with open('model/model.pkl', 'rb') as f:
    model = pickle.load(f)

MODEL_VERSION = "1.0.0"

# Get class labels if available
class_labels = model.classes_.tolist() if hasattr(model, "classes_") else []

def predict_output(user_input: dict):
    df = pd.DataFrame([user_input])

    # Prediction
    predicted_class = model.predict(df)[0]

    response = {
        "predicted_category": predicted_class
    }

    # Probability & confidence (if supported)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(df)[0]
        confidence = max(probabilities)

        class_probs = dict(
            zip(class_labels, [round(p, 4) for p in probabilities])
        )

        response.update({
            "confidence": round(confidence, 4),
            "class_probabilities": class_probs
        })

    return response
