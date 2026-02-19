import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_RAW.mkdir(parents=True, exist_ok=True)

# Load existing data
users = pd.read_csv(DATA_RAW / "users.csv")
cards = pd.read_csv(DATA_RAW / "credit_cards.csv")
payments = pd.read_csv(DATA_RAW / "payments.csv")
billing = pd.read_csv(DATA_RAW / "billing_cycles.csv")

# -----------------------------
# Calculate user-level default rate from payments
# -----------------------------
# Merge to get defaults by card
card_defaults = (
    payments
    .merge(billing[["billing_cycle_id", "card_id"]], on="billing_cycle_id")
    .groupby("card_id")["default_flag"]
    .mean()
    .reset_index()
    .rename(columns={"default_flag": "default_rate"})
)

# Merge with users through cards
user_defaults = (
    cards[["card_id", "user_id"]]
    .merge(card_defaults, on="card_id")
    .groupby("user_id")["default_rate"]
    .mean()
    .reset_index()
)

# Create binary default flag: user defaulted if defauwlt_rate > 30%
user_defaults["default_flag"] = (user_defaults["default_rate"] > 0.15).astype(int)

# -----------------------------
# Generate demographics CORRELATED with defaults
# -----------------------------
demographics = []

for _, row in user_defaults.iterrows():
    user_id = row["user_id"]
    is_defaulter = row["default_flag"]
    
    # Income is correlated with default risk
    if is_defaulter:
        # Defaulters more likely to be low income
        income_band = np.random.choice(
            ["low", "medium", "high"],
            p=[0.60, 0.30, 0.10]  # 60% low, 30% medium, 10% high
        )
    else:
        # Non-defaulters more likely to be higher income
        income_band = np.random.choice(
            ["low", "medium", "high"],
            p=[0.15, 0.40, 0.45]  # 15% low, 40% medium, 45% high
        )
    
    # Age group - younger people slightly more risky
    if is_defaulter:
        age_group = np.random.choice(
            ["18-25", "26-35", "36-50", "51+"],
            p=[0.30, 0.35, 0.25, 0.10]
        )
    else:
        age_group = np.random.choice(
            ["18-25", "26-35", "36-50", "51+"],
            p=[0.15, 0.30, 0.35, 0.20]
        )
    
    # Gender - keep it neutral (no discrimination)
    gender = np.random.choice(["male", "female"])
    
    demographics.append({
        "user_id": user_id,
        "age_group": age_group,
        "gender": gender,
        "income_band": income_band,
        "default_flag": is_defaulter
    })

demographics = pd.DataFrame(demographics)

# -----------------------------
# Save
# -----------------------------
demographics.to_csv(DATA_RAW / "demographics.csv", index=False)

print(f"Demographics generated successfully at:")
print(f"{DATA_RAW / 'demographics.csv'}")
print(f"\nDefault rate by income band:")
print(demographics.groupby("income_band")["default_flag"].mean())
print(f"\nDefault rate by age group:")
print(demographics.groupby("age_group")["default_flag"].mean())
print(f"\nDefault rate by gender:")
print(demographics.groupby("gender")["default_flag"].mean())