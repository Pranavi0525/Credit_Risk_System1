# OpenFinGuard - Column-Level Data Dictionary

**Version:** 2.0  
**Week 2, Day 6**  
**Purpose:** Every column explained with examples and usage classification

---

## 🎯 How to Read This Dictionary

**For each column:**
- **Name:** Column identifier
- **Description:** What it stores in plain English
- **Type:** Data type and size
- **Example:** Real-world sample value
- **Used for:** Classification tag
  - 🎯 **MODEL** = Used for ML prediction features
  - 📊 **REPORTING** = Used for dashboards and analytics
  - ⚖️ **FAIRNESS** = Used for bias detection and fairness analysis
  - 🔗 **RELATIONSHIP** = Primary/foreign keys for joins
  - 📅 **TEMPORAL** = Time tracking for audit/ordering
  - 🚫 **NEVER_FEATURE** = Protected attributes, never use in model

---

## 📊 TABLE 1: users

**Purpose:** Core customer identity table

### Column Details

#### user_id
- **Description:** Unique identifier for each cardholder
- **Type:** VARCHAR(50)
- **Example:** `"USER_00001"`, `"UUID-a3f2-4b8c-9d1e"`
- **Used for:** 🔗 RELATIONSHIP (primary key, links to all other tables)
- **Notes:** Never contains PII; anonymized in production

---

#### account_open_date
- **Description:** Date when customer first opened account with institution
- **Type:** DATE
- **Example:** `2020-03-15` (March 15, 2020)
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Feature:** Account age in days/months (longer tenure may indicate stability)
- **Calculation:** `CURRENT_DATE - account_open_date AS account_age_days`

---

#### account_status
- **Description:** Current status of customer account
- **Type:** VARCHAR(20)
- **Example:** `"active"`, `"closed"`, `"suspended"`
- **Used for:** 📊 REPORTING (filtering)
- **Notes:** Only 'active' accounts used for model training

---

#### created_at
- **Description:** System timestamp when record was created
- **Type:** TIMESTAMP
- **Example:** `2020-03-15 14:32:01.543`
- **Used for:** 📅 TEMPORAL (audit trail)
- **Notes:** Automatically set by database

---

#### updated_at
- **Description:** System timestamp when record was last modified
- **Type:** TIMESTAMP
- **Example:** `2024-01-20 09:15:22.891`
- **Used for:** 📅 TEMPORAL (change tracking)
- **Notes:** Automatically updated via trigger

---

## 📊 TABLE 2: credit_cards

**Purpose:** Individual credit card products

### Column Details

#### card_id
- **Description:** Unique identifier for each credit card
- **Type:** VARCHAR(50)
- **Example:** `"CARD_12345"`, `"CC-a7b3-9f2e"`
- **Used for:** 🔗 RELATIONSHIP (primary key)
- **Notes:** One user can have multiple cards

---

#### user_id
- **Description:** Links card to owning customer
- **Type:** VARCHAR(50)
- **Example:** `"USER_00001"`
- **Used for:** 🔗 RELATIONSHIP (foreign key to users)
- **Notes:** CASCADE DELETE - deleting user deletes all their cards

---

#### credit_limit
- **Description:** Maximum amount customer can borrow on this card
- **Type:** DECIMAL(10, 2)
- **Example:** `5000.00` ($5,000), `10000.00` ($10,000)
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Critical:** Used to calculate credit utilization ratio
- **Feature:** `total_due / credit_limit AS utilization`

---

#### interest_rate
- **Description:** Annual percentage rate (APR) charged on balances
- **Type:** DECIMAL(5, 2)
- **Example:** `18.99` (18.99% APR), `24.99` (24.99% APR)
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Feature:** High interest cards may correlate with risk profile
- **Notes:** Nullable - some promotional cards have 0% intro APR

---

#### card_type
- **Description:** Product category of the card
- **Type:** VARCHAR(30)
- **Example:** `"standard"`, `"premium"`, `"rewards"`, `"cashback"`
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Feature:** Premium cardholders may have different payment behavior
- **Notes:** Categorical feature for one-hot encoding

---

#### issuer
- **Description:** Bank or financial institution that issued the card
- **Type:** VARCHAR(100)
- **Example:** `"Chase Bank"`, `"American Express"`, `"Citibank"`
- **Used for:** 📊 REPORTING (grouping)
- **Notes:** Could be used for multi-issuer analysis

---

#### card_open_date
- **Description:** Date when this specific card was first activated
- **Type:** DATE
- **Example:** `2021-06-10`
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Feature:** Card age (newer cards = less payment history)
- **Calculation:** `observation_date - card_open_date AS card_age_days`

---

#### card_status
- **Description:** Current operational status of card
- **Type:** VARCHAR(20)
- **Example:** `"active"`, `"closed"`, `"frozen"`
- **Used for:** 📊 REPORTING (filtering)
- **Notes:** Only 'active' cards generate billing cycles

---

#### created_at
- **Description:** System timestamp when card record created
- **Type:** TIMESTAMP
- **Example:** `2021-06-10 10:22:15.234`
- **Used for:** 📅 TEMPORAL (audit)

---

#### updated_at
- **Description:** System timestamp when card record last modified
- **Type:** TIMESTAMP
- **Example:** `2024-02-01 16:45:33.901`
- **Used for:** 📅 TEMPORAL (change tracking)
- **Notes:** Tracks credit limit changes, status updates

---

## 📊 TABLE 3: transactions

**Purpose:** All credit card purchase activity

### Column Details

#### transaction_id
- **Description:** Unique identifier for each transaction
- **Type:** VARCHAR(50)
- **Example:** `"TXN_98765"`, `"TX-2024-001234"`
- **Used for:** 🔗 RELATIONSHIP (primary key)
- **Notes:** Highest volume table - millions of rows

---

#### card_id
- **Description:** Which card was used for this transaction
- **Type:** VARCHAR(50)
- **Example:** `"CARD_12345"`
- **Used for:** 🔗 RELATIONSHIP (foreign key to credit_cards)

---

#### transaction_date
- **Description:** **CRITICAL** - Date when purchase occurred
- **Type:** DATE
- **Example:** `2024-03-15`
- **Used for:** 🎯 MODEL + 📅 TEMPORAL
- **Critical:** Must always filter `WHERE transaction_date <= observation_date`
- **Features:** Aggregations over time windows (30d, 60d, 90d spending)

---

#### transaction_time
- **Description:** Optional time of day when transaction occurred
- **Type:** TIME
- **Example:** `14:32:01`, `23:45:12`
- **Used for:** 📊 REPORTING (optional analysis)
- **Potential feature:** Late-night transactions, spending time patterns

---

#### amount
- **Description:** Transaction amount in dollars
- **Type:** DECIMAL(10, 2)
- **Example:** `87.50`, `1250.00`, `12.99`
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Critical:** Core of all spending features
- **Features:** 
  - Total spending: `SUM(amount)`
  - Average transaction: `AVG(amount)`
  - Spending volatility: `STDDEV(amount)`

---

#### merchant_category
- **Description:** Type of merchant/spending category
- **Type:** VARCHAR(50)
- **Example:** `"groceries"`, `"fuel"`, `"entertainment"`, `"restaurants"`, `"travel"`, `"healthcare"`
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Features:**
  - Category concentration (Herfindahl index)
  - High-risk categories (gambling, cash advances)
  - Spending diversity

---

#### merchant_name
- **Description:** Specific store or vendor name
- **Type:** VARCHAR(200)
- **Example:** `"Whole Foods Market"`, `"Shell Gas Station"`, `"Amazon.com"`
- **Used for:** 📊 REPORTING
- **Notes:** Too granular for modeling; use category instead

---

#### transaction_type
- **Description:** Channel through which transaction occurred
- **Type:** VARCHAR(20)
- **Example:** `"online"`, `"in_store"`, `"atm_withdrawal"`
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Feature:** Online vs in-store ratio, ATM withdrawals (cash needs)

---

#### location_city
- **Description:** City where transaction occurred
- **Type:** VARCHAR(100)
- **Example:** `"New York"`, `"Los Angeles"`, `"Chicago"`
- **Used for:** 📊 REPORTING (optional)
- **Potential feature:** Out-of-state transactions (fraud signal)

---

#### location_country
- **Description:** Country where transaction occurred
- **Type:** VARCHAR(50)
- **Example:** `"USA"`, `"Canada"`, `"Mexico"`
- **Used for:** 📊 REPORTING + 🎯 MODEL
- **Feature:** International transaction percentage

---

#### created_at
- **Description:** System timestamp when transaction record created
- **Type:** TIMESTAMP
- **Example:** `2024-03-15 14:32:05.123`
- **Used for:** 📅 TEMPORAL (audit)

---

## 📊 TABLE 4: billing_cycles

**Purpose:** Monthly statement periods - **PRIMARY PREDICTION UNIT**

### Column Details

#### billing_cycle_id
- **Description:** Unique identifier for each monthly statement
- **Type:** VARCHAR(50)
- **Example:** `"CYCLE_2024_03_CARD12345"`, `"BC-2024-Q1-001"`
- **Used for:** 🔗 RELATIONSHIP (primary key)
- **Critical:** One prediction per billing_cycle_id

---

#### card_id
- **Description:** Which card this billing cycle belongs to
- **Type:** VARCHAR(50)
- **Example:** `"CARD_12345"`
- **Used for:** 🔗 RELATIONSHIP (foreign key to credit_cards)

---

#### cycle_start_date
- **Description:** First day of billing period
- **Type:** DATE
- **Example:** `2024-03-01`
- **Used for:** 📅 TEMPORAL + 🎯 MODEL
- **Critical:** Defines window for transaction aggregation
- **Usage:** `WHERE transaction_date BETWEEN cycle_start_date AND cycle_end_date`

---

#### cycle_end_date
- **Description:** Last day of billing period (statement closes)
- **Type:** DATE
- **Example:** `2024-03-31`
- **Used for:** 📅 TEMPORAL + 🎯 MODEL
- **CRITICAL:** This is typically the **observation_date** for predictions
- **Rule:** All features use data ≤ cycle_end_date

---

#### statement_date
- **Description:** Date when statement was generated and sent
- **Type:** DATE
- **Example:** `2024-04-01` (usually day after cycle_end_date)
- **Used for:** 📅 TEMPORAL + 📊 REPORTING
- **Notes:** When customer receives the bill

---

#### due_date
- **Description:** **CRITICAL** - Date by which payment must be received
- **Type:** DATE
- **Example:** `2024-04-21` (typically 21 days after statement_date)
- **Used for:** 🎯 MODEL + 📅 TEMPORAL
- **CRITICAL:** Used to determine if payment was late
- **Calculation:** `payment_date - due_date AS days_late`

---

#### total_due
- **Description:** Total amount owed (statement balance)
- **Type:** DECIMAL(10, 2)
- **Example:** `1250.00`, `3450.75`, `89.50`
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Critical Features:**
  - Credit utilization: `total_due / credit_limit`
  - Payment coverage: `payment_amount / total_due`

---

#### minimum_due
- **Description:** Minimum payment required to avoid late fees
- **Type:** DECIMAL(10, 2)
- **Example:** `25.00` (typically 1-2% of total_due or $25, whichever is higher)
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Feature:** `minimum_due / total_due` (minimum payment ratio)
- **Signal:** Consistently paying only minimum = risk indicator

---

#### previous_balance
- **Description:** Balance carried over from previous billing cycle
- **Type:** DECIMAL(10, 2)
- **Example:** `500.00`, `0.00` (if paid in full last month)
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Feature:** Revolving balance behavior
- **Signal:** Carrying balances month-to-month = potential financial stress

---

#### created_at
- **Description:** System timestamp when billing cycle record created
- **Type:** TIMESTAMP
- **Example:** `2024-04-01 00:05:00.000`
- **Used for:** 📅 TEMPORAL (audit)

---

#### updated_at
- **Description:** System timestamp when billing cycle record modified
- **Type:** TIMESTAMP
- **Example:** `2024-04-01 00:05:00.000`
- **Used for:** 📅 TEMPORAL (change tracking)

---

## 📊 TABLE 5: payments

**Purpose:** Payment events on credit card bills

### Column Details

#### payment_id
- **Description:** Unique identifier for each payment
- **Type:** VARCHAR(50)
- **Example:** `"PAY_87654"`, `"PMT-2024-04-18-001"`
- **Used for:** 🔗 RELATIONSHIP (primary key)

---

#### billing_cycle_id
- **Description:** Which billing cycle this payment applies to
- **Type:** VARCHAR(50)
- **Example:** `"CYCLE_2024_03_CARD12345"`
- **Used for:** 🔗 RELATIONSHIP (foreign key to billing_cycles)
- **Notes:** One billing cycle can have multiple payments

---

#### payment_date
- **Description:** **CRITICAL** - Date when payment was received
- **Type:** DATE
- **Example:** `2024-04-18`, `2024-04-25`
- **Used for:** 🎯 MODEL + 📅 TEMPORAL
- **Critical for labels:** Compare to due_date to determine lateness
- **For features:** Historical payment timing patterns
- **Rule for labels:** Only use payments where `payment_date > observation_date`

---

#### payment_time
- **Description:** Optional time when payment was processed
- **Type:** TIME
- **Example:** `09:15:30`, `23:59:45`
- **Used for:** 📊 REPORTING (optional)
- **Potential feature:** Last-minute payments (close to due date)

---

#### payment_amount
- **Description:** Dollar amount of payment
- **Type:** DECIMAL(10, 2)
- **Example:** `1250.00` (full balance), `25.00` (minimum), `500.00` (partial)
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Critical Features:**
  - Payment ratio: `payment_amount / total_due`
  - Minimum-only pattern: `payment_amount == minimum_due`
  - Full payment pattern: `payment_amount >= total_due`

---

#### payment_method
- **Description:** How payment was made
- **Type:** VARCHAR(30)
- **Example:** `"autopay"`, `"online"`, `"bank_transfer"`, `"check"`, `"phone"`
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Critical Feature:** Autopay = very strong on-time payment indicator
- **Signal:** Manual payments more prone to being missed

---

#### payment_status
- **Description:** Current status of payment
- **Type:** VARCHAR(20)
- **Example:** `"completed"`, `"pending"`, `"failed"`, `"reversed"`
- **Used for:** 🎯 MODEL + 📊 REPORTING
- **Notes:** Only count 'completed' payments for labels
- **Feature:** Failed payment history = major risk signal

---

#### created_at
- **Description:** System timestamp when payment record created
- **Type:** TIMESTAMP
- **Example:** `2024-04-18 09:15:35.456`
- **Used for:** 📅 TEMPORAL (audit)

---

## 📊 TABLE 6: risk_labels ⭐

**Purpose:** TARGET VARIABLE - what we're predicting

### Column Details

#### label_id
- **Description:** Unique identifier for each label
- **Type:** VARCHAR(50)
- **Example:** `"LABEL_2024_03_CARD12345"`
- **Used for:** 🔗 RELATIONSHIP (primary key)

---

#### billing_cycle_id
- **Description:** Which billing cycle this label is for
- **Type:** VARCHAR(50)
- **Example:** `"CYCLE_2024_03_CARD12345"`
- **Used for:** 🔗 RELATIONSHIP (foreign key, UNIQUE constraint)
- **Rule:** Exactly one label per billing cycle

---

#### label_type
- **Description:** What prediction task this label represents
- **Type:** VARCHAR(30)
- **Example:** `"late_30"`, `"late_60"`, `"late_90"`, `"default"`
- **Used for:** 🎯 MODEL (target selection)
- **Details:**
  - `late_30`: Predicting 30+ day delinquency
  - `late_60`: Predicting 60+ day delinquency
  - `late_90`: Predicting 90+ day delinquency
  - `default`: Predicting account default

---

#### observation_date
- **Description:** **THE MOST CRITICAL DATE** - cutoff for features
- **Type:** DATE
- **Example:** `2024-03-31` (typically cycle_end_date)
- **Used for:** 📅 TEMPORAL (defines feature window)
- **RULE:** All features must use data ≤ observation_date
- **Purpose:** Prevents label leakage

---

#### outcome_window_start
- **Description:** First day of outcome observation period
- **Type:** DATE
- **Example:** `2024-04-21` (typically due_date)
- **Used for:** 📅 TEMPORAL (defines label window)
- **Purpose:** When to start looking for payment

---

#### outcome_window_end
- **Description:** Last day of outcome observation period
- **Type:** DATE
- **Example:** `2024-05-21` (for late_30: due_date + 30 days)
- **Used for:** 📅 TEMPORAL (defines label window)
- **Purpose:** Deadline for label determination
- **Calculation varies by label_type:**
  - late_30: `due_date + 30 days`
  - late_60: `due_date + 60 days`
  - late_90: `due_date + 90 days`

---

#### label_value
- **Description:** **TARGET VARIABLE** - actual outcome
- **Type:** VARCHAR(20)
- **Example:** `"on_time"`, `"1-29_dpd"`, `"30-59_dpd"`, `"60-89_dpd"`, `"90+_dpd"`, `"default"`
- **Used for:** 🎯 MODEL (what we're predicting!)
- **Details:**
  - `on_time`: Payment received on or before due_date (0 dpd)
  - `1-29_dpd`: 1-29 days past due (minor late)
  - `30-59_dpd`: 30-59 days past due (moderate delinquency)
  - `60-89_dpd`: 60-89 days past due (serious delinquency)
  - `90+_dpd`: 90+ days past due (severe delinquency)
  - `default`: Account charged off

---

#### days_past_due
- **Description:** Exact number of days payment was late
- **Type:** INTEGER
- **Example:** `0` (on time), `5` (5 days late), `45` (45 days late)
- **Used for:** 🎯 MODEL (regression target option)
- **Calculation:** `first_payment_date - due_date`
- **Notes:** 0 if paid on time or early

---

#### label_date
- **Description:** Date when label was determined/computed
- **Type:** DATE
- **Example:** `2024-05-22` (day after outcome_window_end)
- **Used for:** 📅 TEMPORAL (audit)
- **Purpose:** Track when we finalized the label

---

#### delinquency_status
- **Description:** Legacy field - same as label_value
- **Type:** VARCHAR(20)
- **Example:** Same as label_value
- **Used for:** 🎯 MODEL (backwards compatibility)
- **Notes:** Kept for compatibility, always matches label_value

---

#### notes
- **Description:** Optional human-readable explanation
- **Type:** TEXT
- **Example:** `"Customer called on 2024-04-15, promised payment by 2024-04-20"`
- **Used for:** 📊 REPORTING (documentation)
- **Notes:** Free-text field for context

---

#### created_at
- **Description:** System timestamp when label record created
- **Type:** TIMESTAMP
- **Example:** `2024-05-22 02:00:00.000`
- **Used for:** 📅 TEMPORAL (audit)

---

## 📊 TABLE 7: demographics

**Purpose:** Protected attributes - FAIRNESS ANALYSIS ONLY

### Column Details

#### user_id
- **Description:** Links to user record
- **Type:** VARCHAR(50)
- **Example:** `"USER_00001"`
- **Used for:** 🔗 RELATIONSHIP (primary key and foreign key)

---

#### age_group
- **Description:** Binned age ranges (not exact age)
- **Type:** VARCHAR(20)
- **Example:** `"18-25"`, `"26-35"`, `"36-50"`, `"51-65"`, `"65+"`
- **Used for:** 🚫 NEVER_FEATURE + ⚖️ FAIRNESS
- **CRITICAL:** NEVER use as model feature
- **Purpose:** Post-hoc bias detection only
- **Analysis:** Check if model accuracy varies by age group

---

#### gender
- **Description:** Gender identity
- **Type:** VARCHAR(20)
- **Example:** `"male"`, `"female"`, `"non-binary"`, `"prefer_not_to_say"`
- **Used for:** 🚫 NEVER_FEATURE + ⚖️ FAIRNESS
- **CRITICAL:** NEVER use as model feature
- **Purpose:** Detect gender bias in predictions

---

#### income_band
- **Description:** Binned income ranges (not exact income)
- **Type:** VARCHAR(30)
- **Example:** `"low"`, `"medium"`, `"high"`, `"very_high"`
- **Used for:** 🚫 NEVER_FEATURE + ⚖️ FAIRNESS
- **CRITICAL:** NEVER use as model feature
- **Purpose:** Ensure model doesn't disadvantage low-income users

---

#### education_level
- **Description:** Highest level of education completed
- **Type:** VARCHAR(30)
- **Example:** `"high_school"`, `"bachelors"`, `"masters"`, `"phd"`
- **Used for:** 🚫 NEVER_FEATURE + ⚖️ FAIRNESS
- **Purpose:** Bias detection across education levels

---

#### employment_status
- **Description:** Current employment situation
- **Type:** VARCHAR(30)
- **Example:** `"employed"`, `"self_employed"`, `"unemployed"`, `"student"`, `"retired"`
- **Used for:** 🚫 NEVER_FEATURE + ⚖️ FAIRNESS
- **Purpose:** Fairness across employment types

---

#### marital_status
- **Description:** Marital/relationship status
- **Type:** VARCHAR(20)
- **Example:** `"single"`, `"married"`, `"divorced"`, `"widowed"`
- **Used for:** 🚫 NEVER_FEATURE + ⚖️ FAIRNESS
- **Purpose:** Detect bias based on marital status

---

#### region
- **Description:** Geographic region or state
- **Type:** VARCHAR(50)
- **Example:** `"California"`, `"Texas"`, `"New York"`, `"Midwest"`
- **Used for:** 🚫 NEVER_FEATURE + ⚖️ FAIRNESS
- **Purpose:** Regional fairness analysis

---

#### city_type
- **Description:** Type of residential area
- **Type:** VARCHAR(20)
- **Example:** `"urban"`, `"suburban"`, `"rural"`
- **Used for:** 🚫 NEVER_FEATURE + ⚖️ FAIRNESS
- **Purpose:** Ensure urban/rural fairness

---

#### created_at
- **Description:** System timestamp when demographics record created
- **Type:** TIMESTAMP
- **Example:** `2020-03-15 14:35:00.000`
- **Used for:** 📅 TEMPORAL (audit)

---

#### updated_at
- **Description:** System timestamp when demographics record modified
- **Type:** TIMESTAMP
- **Example:** `2023-11-20 10:22:15.456`
- **Used for:** 📅 TEMPORAL (change tracking)

---

## 🎯 Usage Tag Summary

### 🎯 MODEL (Used in ML Features)
Columns that directly contribute to predictions:
- `credit_limit`, `interest_rate`, `card_type` → Utilization, product features
- `transaction_date`, `amount`, `merchant_category` → Spending patterns
- `total_due`, `minimum_due`, `previous_balance` → Balance behavior
- `payment_date`, `payment_amount`, `payment_method` → Payment patterns
- `account_open_date`, `card_open_date` → Tenure features

### 📊 REPORTING (Business Intelligence)
Columns for dashboards, reports, analysis:
- All status fields: `account_status`, `card_status`, `payment_status`
- Identifiers for grouping: `issuer`, `merchant_name`
- Geographic: `location_city`, `location_country`

### ⚖️ FAIRNESS (Bias Detection Only)
Columns for post-hoc fairness analysis:
- All `demographics` table columns
- **NEVER** join to features
- **ONLY** use after model training

### 🔗 RELATIONSHIP (Keys)
Primary and foreign keys:
- `user_id`, `card_id`, `billing_cycle_id`, `transaction_id`, etc.

### 📅 TEMPORAL (Time Tracking)
Temporal columns for ordering and audit:
- `transaction_date`, `payment_date`, `cycle_end_date` → ML time windows
- `created_at`, `updated_at` → System audit

### 🚫 NEVER_FEATURE (Protected)
**NEVER** use these as model features:
- All `demographics` columns
- Would introduce bias and potentially violate regulations

---

## 📖 Quick Reference: Most Important Columns

### For Prediction (Features)
1. **credit_limit** - Calculate utilization
2. **total_due** - Current balance
3. **transaction_date** + **amount** - Spending patterns
4. **payment_date** - Payment timing history
5. **payment_method** - Autopay indicator
6. **cycle_end_date** - Observation date

### For Labels (Target)
1. **label_value** - What we're predicting
2. **observation_date** - Feature cutoff (≤)
3. **outcome_window_start/end** - Label period (>)
4. **days_past_due** - Regression target option

### For Fairness (Bias Detection)
1. **age_group** - Age-based fairness
2. **gender** - Gender bias detection
3. **income_band** - Socioeconomic fairness
4. **region** - Geographic bias

---

## ✅ Data Dictionary Best Practices

1. **Always check the "Used for" tag** before using a column
2. **Never use 🚫 NEVER_FEATURE columns** in model training
3. **Always respect temporal boundaries** for 📅 TEMPORAL columns
4. **Use examples** to understand expected values
5. **Reference this document** when writing SQL queries

---

**This column-level dictionary ensures everyone understands exactly what each field means and how it should be used!** 📚