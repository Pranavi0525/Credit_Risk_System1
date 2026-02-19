from .celery_worker import celery_app
import pandas as pd
import joblib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "credit_risk_model.pkl"
model = joblib.load(MODEL_PATH)

@celery_app.task(name="src.api.tasks.predict_async")
def predict_async(features: dict):

    df = pd.DataFrame([features])
    probability = model.predict_proba(df)[0][1]

    risk_category = (
        "High Risk" if probability > 0.7
        else "Medium Risk" if probability > 0.3
        else "Low Risk"
    )

    return {
        "default_probability": float(probability),
        "risk_category": risk_category
    }
