import pandas as pd
import numpy as np
from datetime import date, timedelta
from pathlib import Path

np.random.seed(42)

# -----------------------------
# Paths (robust)
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_RAW.mkdir(parents=True, exist_ok=True)

# -----------------------------
# USERS TABLE
# -----------------------------
users = pd.DataFrame({
    "user_id": [f"user_{i}" for i in range(1, 21)],
    "account_open_date": [
        date.today() - timedelta(days=np.random.randint(300, 2000))
        for _ in range(20)
    ],
    "account_status": ["active"] * 20
})

# -----------------------------
# CREDIT CARDS TABLE
# -----------------------------
cards = pd.DataFrame({
    "card_id": [f"card_{i}" for i in range(1, 31)],
    "user_id": np.random.choice(users["user_id"], 30),
    "credit_limit": np.random.choice([50000, 100000, 200000], 30),
    "interest_rate": np.random.uniform(12, 36, 30).round(2),
    "card_open_date": [
        date.today() - timedelta(days=np.random.randint(200, 1500))
        for _ in range(30)
    ],
    "card_status": ["active"] * 30
})

# -----------------------------
# BILLING CYCLES
# -----------------------------
billing_cycles = []

for card in cards["card_id"]:
    for m in range(6):
        cycle_end = date.today().replace(day=1) - timedelta(days=30*m)
        cycle_start = cycle_end - timedelta(days=30)

        total_due = np.random.randint(1000, 30000)
        minimum_due = int(total_due * np.random.uniform(0.05, 0.15))  # 5-15% of total
        billing_cycles.append({
            "billing_cycle_id": f"{card}_{m}",
            "card_id": card,
            "cycle_start_date": cycle_start,
            "cycle_end_date": cycle_end,
            "statement_date": cycle_end + timedelta(days=1),
            "due_date": cycle_end + timedelta(days=21),
            "total_due": total_due,
            "minimum_due": minimum_due
        })

billing_cycles = pd.DataFrame(billing_cycles)

# -----------------------------
# TRANSACTIONS TABLE
# -----------------------------
transaction_rows = []

merchant_categories = [
    "groceries", "fuel", "rent", "utilities",
    "entertainment", "travel", "shopping", "food_delivery"
]

for _, cycle in billing_cycles.iterrows():
    num_txns = np.random.randint(10, 60)

    for i in range(num_txns):
        txn_date = cycle["cycle_start_date"] + timedelta(
            days=np.random.randint(0, 30)
        )

        amount = np.random.choice(
            [100, 200, 500, 1000, 2000, 5000],
            p=[0.2, 0.25, 0.25, 0.15, 0.1, 0.05]
        )

        transaction_rows.append({
            "transaction_id": f"txn_{cycle['billing_cycle_id']}_{i}",
            "card_id": cycle["card_id"],
            "transaction_date": txn_date,
            "amount": amount,
            "merchant_category": np.random.choice(merchant_categories),
            "transaction_type": np.random.choice(["online", "in_store"], p=[0.6, 0.4])
        })

transactions = pd.DataFrame(transaction_rows)

# -----------------------------
# PAYMENTS TABLE WITH REALISTIC DEFAULTS
# -----------------------------
payment_rows = []

# Assign risk profiles to cards (some cards will be riskier)
card_risk_profile = {}
for card in cards["card_id"].unique():
    # 20% high risk, 30% medium risk, 50% low risk
    card_risk_profile[card] = np.random.choice(
        ["high_risk", "medium_risk", "low_risk"],
        p=[0.2, 0.3, 0.5]
    )

for _, cycle in billing_cycles.iterrows():
    card_id = cycle["card_id"]
    risk = card_risk_profile[card_id]
    
    # Payment timing based on risk profile
    if risk == "high_risk":
        # Often late, sometimes very late
        days_offset = int(np.random.choice(
            [-5, 0, 5, 15, 30, 60, 120],
            p=[0.05, 0.10, 0.15, 0.20, 0.25, 0.15, 0.10])
        )
    elif risk == "medium_risk":
        # Sometimes late
        days_offset = np.random.choice(
            [-5, 0, 5, 15, 30],
            p=[0.10, 0.30, 0.30, 0.20, 0.10]
        )
    else:  # low_risk
        # Usually on time
        days_offset = np.random.choice(
            [-5, 0, 5],
            p=[0.30, 0.60, 0.10]
        )
    
    payment_date = cycle["due_date"] + timedelta(days=int(days_offset))
    
    min_due = int(cycle["minimum_due"])
    total_due = int(cycle["total_due"])
    
    # Payment amount based on risk profile
    if risk == "high_risk":
        # Often pay only minimum or less
        payment_choices = [
            min_due * 0.8,  # Less than minimum
            min_due,        # Exactly minimum
            min_due * 1.5,  # Bit more than minimum
            total_due       # Full payment (rare)
        ]
        payment_amount = int(np.random.choice(
            payment_choices,
            p=[0.15, 0.50, 0.30, 0.05]
        ))
    elif risk == "medium_risk":
        payment_amount = int(np.random.choice(
            [min_due, total_due * 0.5, total_due],
            p=[0.30, 0.40, 0.30]
        ))
    else:  # low_risk
        # Usually pay in full
        payment_amount = int(np.random.choice(
            [min_due, total_due],
            p=[0.20, 0.80]
        ))
    
    # Ensure payment amount is positive and within reasonable bounds
    payment_amount = max(0, min(payment_amount, total_due + 1000))
    
    payment_rows.append({
        "payment_id": f"pay_{cycle['billing_cycle_id']}",
        "billing_cycle_id": cycle["billing_cycle_id"],
        "payment_date": payment_date,
        "payment_amount": payment_amount,
        "payment_status": "completed"
    })

payments = pd.DataFrame(payment_rows)

# -----------------------------
# ADD DEFAULT FLAGS
# -----------------------------
# Calculate days late for each payment
payments["days_late"] = (
    pd.to_datetime(payments["payment_date"]) - 
    pd.to_datetime(billing_cycles.set_index("billing_cycle_id").loc[payments["billing_cycle_id"], "due_date"].values)
).dt.days

billing_min_due = billing_cycles.set_index("billing_cycle_id")["minimum_due"]

# Determine default: 90+ days late OR paid less than minimum due
payments["default_flag"] = (
    (payments["days_late"] > 90) | 
    (payments["payment_amount"] < billing_min_due.loc[payments["billing_cycle_id"]].values)
).astype(int)
# Get minimum due for each billing cycle
billing_min_due = billing_cycles.set_index("billing_cycle_id")["minimum_due"]

# Determine default: 90+ days late OR paid less than minimum due
payments["default_flag"] = (
    (payments["days_late"] > 90) | 
    (payments["payment_amount"] < billing_min_due.loc[payments["billing_cycle_id"]].values)
).astype(int)

# -----------------------------
# SAVE FILES
# -----------------------------
users.to_csv(DATA_RAW / "users.csv", index=False)
cards.to_csv(DATA_RAW / "credit_cards.csv", index=False)
billing_cycles.to_csv(DATA_RAW / "billing_cycles.csv", index=False)
transactions.to_csv(DATA_RAW / "transactions.csv", index=False)
payments.to_csv(DATA_RAW / "payments.csv", index=False)

print("✅ Synthetic base tables generated successfully.")
print("✅ Transactions generated.")
print("✅ Payments generated.")
print(f"✅ Default rate: {payments['default_flag'].mean():.2%}")
print(f"   Total payments: {len(payments)}")
print(f"   Defaults: {payments['default_flag'].sum()}")