# Data Sources, Entities & Relationships

This document defines the core entities (tables) required for the Credit Card Early Warning System.
The schema is designed to support behavioral risk modeling, temporal analysis, and fairness evaluation.

---

## 1. users

**Description**  
Represents a unique individual who owns one or more credit cards.

**Primary Key**
- user_id

**Key Attributes**
- user_id
- account_open_date
- account_status (active, closed, suspended)

**Temporal Nature**
- Mostly static
- Account status can change over time

**Sensitivity**
- Medium (PII risk when joined with demographics)

**Relationships**
- One user → many credit_cards
- One user → many billing_cycles (indirect via cards)
- One user → many risk_labels

---

## 2. credit_cards

**Description**  
Represents individual credit cards issued to users.

**Primary Key**
- card_id

**Foreign Key**
- user_id → users.user_id

**Key Attributes**
- card_id
- user_id
- credit_limit
- card_open_date
- card_status

**Temporal Nature**
- Credit limit and status may change over time

**Sensitivity**
- High (financial exposure)

**Relationships**
- One user → many credit_cards
- One credit_card → many transactions
- One credit_card → many billing_cycles
- One credit_card → many payments

---

## 3. transactions

**Description**  
Represents all spending activity on credit cards.

**Primary Key**
- transaction_id

**Foreign Key**
- card_id → credit_cards.card_id

**Key Attributes**
- transaction_id
- card_id
- transaction_date
- amount
- merchant_category
- transaction_type (online/offline)

**Temporal Nature**
- Fully time-dependent (event-based)

**Sensitivity**
- High (behavioral and financial data)

**Relationships**
- One credit_card → many transactions

---

## 4. billing_cycles

**Description**  
Represents monthly billing periods for each credit card.

**Primary Key**
- billing_cycle_id

**Foreign Key**
- card_id → credit_cards.card_id

**Key Attributes**
- billing_cycle_id
- card_id
- cycle_start_date
- cycle_end_date
- total_due
- minimum_due
- due_date

**Temporal Nature**
- Fully time-dependent (monthly snapshots)

**Sensitivity**
- High (financial obligations)

**Relationships**
- One credit_card → many billing_cycles
- One billing_cycle → many payments
- One billing_cycle → one risk_label

---

## 5. payments

**Description**  
Represents payments made by users toward their credit card bills.

**Primary Key**
- payment_id

**Foreign Key**
- billing_cycle_id → billing_cycles.billing_cycle_id

**Key Attributes**
- payment_id
- billing_cycle_id
- payment_date
- payment_amount
- payment_method

**Temporal Nature**
- Event-based, time-dependent

**Sensitivity**
- High (financial behavior)

**Relationships**
- One billing_cycle → many payments

---

## 6. risk_labels (Target Variable)

**Description**  
Defines the payment outcome for a billing cycle.
This is the supervised learning target.

**Primary Key**
- label_id

**Foreign Key**
- billing_cycle_id → billing_cycles.billing_cycle_id

**Key Attributes**
- label_id
- billing_cycle_id
- delinquency_status (on_time, 30_dpd, 60_dpd, 90_dpd)
- label_date

**Temporal Nature**
- Time-dependent (per billing cycle)

**Sensitivity**
- High (credit risk classification)

**Relationships**
- One billing_cycle → one risk_label

---

## 7. demographics

**Description**  
Contains demographic attributes used strictly for fairness and bias analysis.
This table is never used directly for prediction.

**Primary Key**
- user_id

**Foreign Key**
- user_id → users.user_id

**Key Attributes**
- age_group
- gender
- income_band
- region

**Temporal Nature**
- Slowly changing

**Sensitivity**
- Very High (protected attributes)

**Relationships**
- One user → one demographics record

---

## Summary of Core Relationships

- users 1 → N credit_cards
- credit_cards 1 → N transactions
- credit_cards 1 → N billing_cycles
- billing_cycles 1 → N payments
- billing_cycles 1 → 1 risk_labels
- users 1 → 1 demographics

This schema supports:
- Behavioral risk modeling
- Time-series feature engineering
- Ethical and fairness evaluation
