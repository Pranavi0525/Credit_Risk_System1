import pandas as pd
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Load Data
# -----------------------------
billing = pd.read_csv(DATA_RAW / "billing_cycles.csv")
payments = pd.read_csv(DATA_RAW / "payments.csv")
cards = pd.read_csv(DATA_RAW / "credit_cards.csv")
demographics = pd.read_csv(DATA_RAW / "demographics.csv")

# Convert dates
billing["due_date"] = pd.to_datetime(billing["due_date"])
payments["payment_date"] = pd.to_datetime(payments["payment_date"])

# -----------------------------
# Merge Data
# -----------------------------
# Start with payments (which already has default_flag!)
data = payments.merge(billing, on="billing_cycle_id")
data = data.merge(cards[["card_id", "credit_limit", "user_id"]], on="card_id")
data = data.merge(demographics[["user_id", "income_band", "age_group"]], on="user_id")

# -----------------------------
# Feature Engineering
# -----------------------------
# Payment behavior features
data["payment_delay"] = data["days_late"]  # Use the days_late we already calculated
data["payment_ratio"] = data["payment_amount"] / data["total_due"]
data["min_payment_ratio"] = data["payment_amount"] / data["minimum_due"]
data["utilization"] = data["total_due"] / data["credit_limit"]

# Aggregate features by user
user_features = data.groupby("user_id").agg({
    "payment_delay": ["mean", "max", "std"],
    "payment_ratio": ["mean", "min"],
    "utilization": ["mean", "max"],
    "default_flag": "max"  # User is defaulter if ANY payment defaulted
}).reset_index()

# Flatten column names
user_features.columns = [
    "user_id",
    "avg_payment_delay",
    "max_payment_delay", 
    "std_payment_delay",
    "avg_payment_ratio",
    "min_payment_ratio",
    "avg_utilization",
    "max_utilization",
    "default_flag"
]

# Fill NaN values (std might be NaN for users with only 1 payment)
user_features["std_payment_delay"] = user_features["std_payment_delay"].fillna(0)

# Add demographic features
user_features = user_features.merge(
    demographics[["user_id", "income_band", "age_group"]], 
    on="user_id"
)

# Encode categorical variables
user_features["income_low"] = (user_features["income_band"] == "low").astype(int)
user_features["income_medium"] = (user_features["income_band"] == "medium").astype(int)
user_features["income_high"] = (user_features["income_band"] == "high").astype(int)

user_features["age_18_25"] = (user_features["age_group"] == "18-25").astype(int)
user_features["age_26_35"] = (user_features["age_group"] == "26-35").astype(int)
user_features["age_36_50"] = (user_features["age_group"] == "36-50").astype(int)
user_features["age_51_plus"] = (user_features["age_group"] == "51+").astype(int)

# -----------------------------
# Save Features
# -----------------------------
user_features.to_csv(DATA_PROCESSED / "model_features.csv", index=False)

print("✅ Feature engineering complete!")
print(f"   Total users: {len(user_features)}")
print(f"   Features created: {len(user_features.columns) - 2}")  # Exclude user_id and default_flag
print(f"   Default rate: {user_features['default_flag'].mean():.2%}")
print(f"   Defaulters: {user_features['default_flag'].sum()}")