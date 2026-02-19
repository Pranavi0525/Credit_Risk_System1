import pandas as pd
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
import joblib
import time
from datetime import datetime
import logging

from .tasks import  predict_async
from .database import engine, get_db
from .models import Base, PredictionLog
from .cache import generate_key, get_cache, set_cache
from celery.result import AsyncResult
from .celery_worker import celery_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "credit_risk_model.pkl"
model = joblib.load(MODEL_PATH)
logger.info(f"✅ Model loaded from {MODEL_PATH}")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Credit Risk API", version="1.0", description="Production Credit Risk Scoring Service")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time}ms")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"ERROR at {request.url.path}: {str(exc)}")
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

@app.get("/")
def home():
    return {"message": "Credit Risk API is running 🚀"}

@app.get("/v1/health")
def health_check():
    return {"status": "healthy", "model_loaded": True}

@app.get("/v1/model-info")
def model_info():
    return {
        "model_name": "Credit Risk Logistic Regression",
        "version": "1.0",
        "trained_on": "Synthetic Credit Data",
        "features_used": len(model.feature_names_in_),
        "status": "ready",
        "timestamp": datetime.now()
    }

class UserFeatures(BaseModel):
    avg_payment_delay: float
    max_payment_delay: float
    std_payment_delay: float
    avg_payment_ratio: float
    min_payment_ratio: float
    avg_utilization: float
    max_utilization: float
    income_low: int
    income_medium: int
    age_18_25: int
    age_26_35: int
    age_36_50: int

@app.post("/v1/predict")
def predict_risk(features: UserFeatures, db: Session = Depends(get_db)):
    input_data = features.dict()
    cache_key = generate_key(input_data)
    cached = get_cache(cache_key)
    if cached:
        logger.info("⚡ CACHE HIT — Returned from Redis")
        return cached
    logger.info("❌ CACHE MISS — Running Model")
    df = pd.DataFrame([input_data])
    probability = model.predict_proba(df)[0][1]
    risk_category = (
        "High Risk" if probability > 0.7
        else "Medium Risk" if probability > 0.3
        else "Low Risk"
    )
    result = {
        "default_probability": float(probability),
        "risk_category": risk_category
    }
    log = PredictionLog(
        **input_data,
        default_probability=result["default_probability"],
        risk_category=result["risk_category"]
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    result["saved_record_id"] = log.id
    set_cache(cache_key, result)
    return result

@app.post("/v1/predict-async")
def predict_async_endpoint(features: UserFeatures):
    task = predict_async.delay(features.dict())
    return {
        "task_id": task.id,
        "status": "Processing"
    }