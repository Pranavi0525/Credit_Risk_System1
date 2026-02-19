import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# -----------------------------
# Load Features
# -----------------------------
features = pd.read_csv(DATA_PROCESSED / "model_features.csv")

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

# -----------------------------
# Train final model on ALL data
# -----------------------------
model = LogisticRegression(max_iter=1000)
model.fit(X, y)

# -----------------------------
# Predict probabilities
# -----------------------------
features["default_probability"] = model.predict_proba(X)[:, 1]

# -----------------------------
# Convert to Credit Score
# -----------------------------
features["credit_score"] = 900 - (features["default_probability"] * 600)
features["credit_score"] = features["credit_score"].astype(int)

# -----------------------------
# Risk Categories
# -----------------------------
def assign_risk(score):
    if score >= 800:
        return "Excellent"
    elif score >= 700:
        return "Good"
    elif score >= 600:
        return "Fair"
    elif score >= 500:
        return "Poor"
    else:
        return "Very Risky"

features["risk_category"] = features["credit_score"].apply(assign_risk)

# -----------------------------
# Save report
# -----------------------------
output_cols = [
    "user_id",
    "credit_score",
    "risk_category",
    "default_probability"
]

features[output_cols].to_csv(
    DATA_PROCESSED / "credit_scores.csv",
    index=False
)

print("\n✅ CREDIT SCORING COMPLETE!")
print(features[output_cols].head())

print("\nScore Distribution:")
print(features["risk_category"].value_counts())
