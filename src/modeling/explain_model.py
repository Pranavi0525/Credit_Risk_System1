import shap
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# Load features
features = pd.read_csv(DATA_PROCESSED / "model_features.csv")

feature_cols = [
    "avg_payment_delay","max_payment_delay","std_payment_delay",
    "avg_payment_ratio","min_payment_ratio",
    "avg_utilization","max_utilization",
    "income_low","income_medium",
    "age_18_25","age_26_35","age_36_50"
]

X = features[feature_cols]
y = features["default_flag"]

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X, y)

# SHAP explainability
explainer = shap.LinearExplainer(model, X)
shap_values = explainer.shap_values(X)

# Summary
print("\nTop Risk Drivers:")
importance = pd.DataFrame({
    "feature": feature_cols,
    "impact": abs(shap_values).mean(axis=0)
}).sort_values("impact", ascending=False)

print(importance)
