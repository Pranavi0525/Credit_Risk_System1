import joblib
from pathlib import Path
import pandas as pd
from sklearn.linear_model import LogisticRegression

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

features = pd.read_csv(DATA_PROCESSED / "model_features.csv")

# SAME FEATURE LIST as training
feature_cols = [
    "avg_payment_delay",
    "max_payment_delay",
    "std_payment_delay",
    "avg_payment_ratio",
    "min_payment_ratio",
    "avg_utilization",
    "max_utilization",
    "income_low",
    "income_medium",
    "age_18_25",
    "age_26_35",
    "age_36_50"
]

X = features[feature_cols]
y = features["default_flag"]

model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X, y)

joblib.dump(model, MODEL_DIR / "credit_risk_model.pkl")

print("✅ Model saved successfully!")
print(f"Saved at: {MODEL_DIR / 'credit_risk_model.pkl'}")
