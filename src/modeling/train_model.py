import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
import numpy as np

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# -----------------------------
# Load engineered features
# -----------------------------
features = pd.read_csv(DATA_PROCESSED / "model_features.csv")

print(f"Loaded {len(features)} users")
print(f"Default rate: {features['default_flag'].mean():.2%}")
print(f"Defaulters: {features['default_flag'].sum()}")

# -----------------------------
# Prepare features
# -----------------------------
# Select feature columns
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

# Check class distribution
print(f"\nClass distribution:")
print(f"Non-defaulters: {(y == 0).sum()}")
print(f"Defaulters: {(y == 1).sum()}")

# Only proceed if we have both classes
if y.sum() == 0 or y.sum() == len(y):
    print("\n⚠️  ERROR: Only one class present in data!")
    print("Run the data generation scripts again to create defaults.")
else:
    # -----------------------------
    # Split data
    # -----------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")

    # -----------------------------
    # Train model
    # -----------------------------
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    # -----------------------------
    # Evaluate
    # -----------------------------
    preds_proba = model.predict_proba(X_test)[:, 1]
    preds = model.predict(X_test)

    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    
    if len(np.unique(y_test)) > 1:
        print(f"\nROC-AUC Score: {roc_auc_score(y_test, preds_proba):.4f}")
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, preds))
    
    print("\nClassification Report:")
    print(classification_report(y_test, preds))

    # -----------------------------
    # Feature Importance
    # -----------------------------
    print("\n" + "="*50)
    print("FEATURE IMPORTANCE (Coefficients)")
    print("="*50)
    
    coef_df = pd.DataFrame({
        'feature': feature_cols,
        'coefficient': model.coef_[0]
    }).sort_values('coefficient', key=abs, ascending=False)
    
    print(coef_df.to_string(index=False))
    
    print("\n✅ Model training complete!")
import joblib

MODEL_PATH = DATA_PROCESSED / "credit_model.pkl"
joblib.dump(model, MODEL_PATH)

print("✅ Model saved!")
