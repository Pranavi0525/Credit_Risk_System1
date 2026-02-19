import pandas as pd
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"

# -----------------------------
# Load Data
# -----------------------------
demographics = pd.read_csv(DATA_RAW / "demographics.csv")

# Make sure default_flag exists
if "default_flag" not in demographics.columns:
    print("ERROR: default_flag not found in demographics!")
    print("Available columns:", demographics.columns.tolist())
else:
    # Fill any NaN values
    demographics["default_flag"] = demographics["default_flag"].fillna(0).astype(int)
    
    # -----------------------------
    # Fairness Analysis
    # -----------------------------
    print("===== DEFAULT RATE BY GENDER =====")
    print(demographics.groupby("gender")["default_flag"].mean())
    
    print("\n===== DEFAULT RATE BY INCOME =====")
    print(demographics.groupby("income_band")["default_flag"].mean())
    
    print("\n===== DEFAULT RATE BY AGE GROUP =====")
    print(demographics.groupby("age_group")["default_flag"].mean())
    
    # -----------------------------
    # Statistical Summary
    # -----------------------------
    print("\n===== OVERALL STATISTICS =====")
    print(f"Total users: {len(demographics)}")
    print(f"Total defaulters: {demographics['default_flag'].sum()}")
    print(f"Overall default rate: {demographics['default_flag'].mean():.2%}")