from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from .database import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)

    avg_payment_delay = Column(Float)
    max_payment_delay = Column(Float)
    std_payment_delay = Column(Float)

    avg_payment_ratio = Column(Float)
    min_payment_ratio = Column(Float)

    avg_utilization = Column(Float)
    max_utilization = Column(Float)

    income_low = Column(Integer)
    income_medium = Column(Integer)

    age_18_25 = Column(Integer)
    age_26_35 = Column(Integer)
    age_36_50 = Column(Integer)

    default_probability = Column(Float)
    risk_category = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
