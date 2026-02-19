-- ============================================================================
-- OpenFinGuard - Credit Intelligence Platform
-- Schema Definition v1.0
-- 
-- Purpose: Core database schema for credit card risk prediction system
-- Design Principles:
--   1. All tables have time columns for temporal analysis
--   2. No derived columns (calculate at query/feature time)
--   3. Clear foreign key relationships
--   4. Support for both behavioral modeling and fairness analysis
-- ============================================================================

-- ============================================================================
-- TABLE 1: users
-- Description: Core user/cardholder entities
-- Granularity: One record per unique user
-- Temporal: Mostly static, status can change
-- ============================================================================

CREATE TABLE users (
    user_id             VARCHAR(50) PRIMARY KEY,
    account_open_date   DATE NOT NULL,
    account_status      VARCHAR(20) NOT NULL,  -- 'active', 'closed', 'suspended'
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_account_status CHECK (account_status IN ('active', 'closed', 'suspended'))
);

-- Index for status queries
CREATE INDEX idx_users_status ON users(account_status);
CREATE INDEX idx_users_open_date ON users(account_open_date);

COMMENT ON TABLE users IS 'Core user entities - one record per cardholder';
COMMENT ON COLUMN users.user_id IS 'Unique identifier for each user';
COMMENT ON COLUMN users.account_open_date IS 'Date when user first opened account';
COMMENT ON COLUMN users.account_status IS 'Current status: active, closed, or suspended';


-- ============================================================================
-- TABLE 2: credit_cards
-- Description: Individual credit cards issued to users
-- Granularity: One record per credit card
-- Temporal: Credit limit and status may change over time
-- Relationship: Many cards per user possible
-- ============================================================================

CREATE TABLE credit_cards (
    card_id             VARCHAR(50) PRIMARY KEY,
    user_id             VARCHAR(50) NOT NULL,
    credit_limit        DECIMAL(10, 2) NOT NULL,  -- No derived utilization here
    interest_rate       DECIMAL(5, 2),            -- Annual percentage rate
    card_type           VARCHAR(30),              -- 'standard', 'premium', 'rewards'
    issuer              VARCHAR(100),             -- Bank/institution name
    card_open_date      DATE NOT NULL,
    card_status         VARCHAR(20) NOT NULL,     -- 'active', 'closed', 'frozen'
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_card_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_credit_limit CHECK (credit_limit > 0),
    CONSTRAINT chk_interest_rate CHECK (interest_rate >= 0 AND interest_rate <= 100),
    CONSTRAINT chk_card_status CHECK (card_status IN ('active', 'closed', 'frozen'))
);

-- Indexes for common queries
CREATE INDEX idx_cards_user ON credit_cards(user_id);
CREATE INDEX idx_cards_status ON credit_cards(card_status);
CREATE INDEX idx_cards_open_date ON credit_cards(card_open_date);

COMMENT ON TABLE credit_cards IS 'Individual credit cards - multiple cards per user allowed';
COMMENT ON COLUMN credit_cards.credit_limit IS 'Maximum credit available on this card';
COMMENT ON COLUMN credit_cards.interest_rate IS 'APR as percentage (e.g., 18.99)';


-- ============================================================================
-- TABLE 3: transactions
-- Description: All spending activity on credit cards
-- Granularity: One record per transaction
-- Temporal: Fully time-dependent (event-based)
-- Volume: Highest volume table
-- ============================================================================

CREATE TABLE transactions (
    transaction_id      VARCHAR(50) PRIMARY KEY,
    card_id             VARCHAR(50) NOT NULL,
    transaction_date    DATE NOT NULL,
    transaction_time    TIME,                    -- Optional: time of day
    amount              DECIMAL(10, 2) NOT NULL,
    merchant_category   VARCHAR(50),             -- 'groceries', 'fuel', 'entertainment', etc.
    merchant_name       VARCHAR(200),
    transaction_type    VARCHAR(20),             -- 'online', 'in_store', 'atm_withdrawal'
    location_city       VARCHAR(100),
    location_country    VARCHAR(50),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_txn_card FOREIGN KEY (card_id) 
        REFERENCES credit_cards(card_id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_txn_amount CHECK (amount >= 0),
    CONSTRAINT chk_txn_type CHECK (transaction_type IN ('online', 'in_store', 'atm_withdrawal', 'other'))
);

-- Critical indexes for time-series analysis
CREATE INDEX idx_txn_card ON transactions(card_id);
CREATE INDEX idx_txn_date ON transactions(transaction_date);
CREATE INDEX idx_txn_card_date ON transactions(card_id, transaction_date);  -- Composite for windowing
CREATE INDEX idx_txn_category ON transactions(merchant_category);

COMMENT ON TABLE transactions IS 'All credit card spending events - event-based temporal data';
COMMENT ON COLUMN transactions.transaction_date IS 'Date of transaction - critical for time-series features';
COMMENT ON COLUMN transactions.merchant_category IS 'Spending category for behavioral analysis';


-- ============================================================================
-- TABLE 4: billing_cycles
-- Description: Monthly billing periods for each card
-- Granularity: One record per card per month
-- Temporal: Monthly snapshots of billing state
-- Note: This is the primary unit for prediction
-- ============================================================================

CREATE TABLE billing_cycles (
    billing_cycle_id    VARCHAR(50) PRIMARY KEY,
    card_id             VARCHAR(50) NOT NULL,
    cycle_start_date    DATE NOT NULL,
    cycle_end_date      DATE NOT NULL,
    statement_date      DATE NOT NULL,            -- When statement was generated
    due_date            DATE NOT NULL,            -- Payment due date
    total_due           DECIMAL(10, 2) NOT NULL,  -- Total amount owed
    minimum_due         DECIMAL(10, 2) NOT NULL,  -- Minimum payment required
    previous_balance    DECIMAL(10, 2),           -- Balance carried from previous cycle
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_billing_card FOREIGN KEY (card_id) 
        REFERENCES credit_cards(card_id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_cycle_dates CHECK (cycle_end_date > cycle_start_date),
    CONSTRAINT chk_due_after_end CHECK (due_date > cycle_end_date),
    CONSTRAINT chk_total_due CHECK (total_due >= 0),
    CONSTRAINT chk_minimum_due CHECK (minimum_due >= 0 AND minimum_due <= total_due)
);

-- Indexes for cycle lookups
CREATE INDEX idx_billing_card ON billing_cycles(card_id);
CREATE INDEX idx_billing_cycle_dates ON billing_cycles(cycle_start_date, cycle_end_date);
CREATE INDEX idx_billing_due_date ON billing_cycles(due_date);

COMMENT ON TABLE billing_cycles IS 'Monthly billing periods - primary unit for risk prediction';
COMMENT ON COLUMN billing_cycles.due_date IS 'Critical date for payment delay calculation';
COMMENT ON COLUMN billing_cycles.total_due IS 'Full statement balance - not derived, stored as fact';


-- ============================================================================
-- TABLE 5: payments
-- Description: All payments made toward credit card bills
-- Granularity: One record per payment event
-- Temporal: Event-based, can have multiple payments per billing cycle
-- ============================================================================

CREATE TABLE payments (
    payment_id          VARCHAR(50) PRIMARY KEY,
    billing_cycle_id    VARCHAR(50) NOT NULL,
    payment_date        DATE NOT NULL,
    payment_time        TIME,                     -- Optional: time of payment
    payment_amount      DECIMAL(10, 2) NOT NULL,
    payment_method      VARCHAR(30),              -- 'bank_transfer', 'check', 'online', 'autopay'
    payment_status      VARCHAR(20) NOT NULL,     -- 'completed', 'pending', 'failed', 'reversed'
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_payment_billing FOREIGN KEY (billing_cycle_id) 
        REFERENCES billing_cycles(billing_cycle_id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_payment_amount CHECK (payment_amount > 0),
    CONSTRAINT chk_payment_status CHECK (payment_status IN ('completed', 'pending', 'failed', 'reversed'))
);

-- Indexes for payment analysis
CREATE INDEX idx_payment_billing ON payments(billing_cycle_id);
CREATE INDEX idx_payment_date ON payments(payment_date);
CREATE INDEX idx_payment_billing_date ON payments(billing_cycle_id, payment_date);
CREATE INDEX idx_payment_status ON payments(payment_status);

COMMENT ON TABLE payments IS 'Payment events - multiple payments per billing cycle allowed';
COMMENT ON COLUMN payments.payment_date IS 'Actual date payment was made - compare to due_date for delays';
COMMENT ON COLUMN payments.payment_status IS 'Track payment completion for risk analysis';


-- ============================================================================
-- TABLE 6: risk_labels
-- Description: Target variable for supervised learning
-- Granularity: One record per billing cycle
-- Temporal: Determined after billing cycle completion
-- Note: This is what we're trying to PREDICT
-- 
-- CRITICAL: LABEL LEAKAGE PREVENTION
-- "The label is computed AFTER the observation window."
-- 
-- Timeline:
-- |--- Observation Period ---|--- Outcome Window ---|
--                             ↑                      ↑
--                     observation_date    outcome_window_end
-- 
-- Features use data ≤ observation_date
-- Label uses data > observation_date and ≤ outcome_window_end
-- ============================================================================

CREATE TABLE risk_labels (
    label_id            VARCHAR(50) PRIMARY KEY,
    billing_cycle_id    VARCHAR(50) NOT NULL UNIQUE,  -- One label per cycle
    
    -- Label type and value
    label_type          VARCHAR(30) NOT NULL,         -- Type: 'late_30', 'late_60', 'late_90', 'default'
    label_value         VARCHAR(20) NOT NULL,         -- Actual outcome: 'on_time', '1-29_dpd', etc.
    
    -- Temporal boundaries (CRITICAL for preventing label leakage)
    observation_date        DATE NOT NULL,            -- Cutoff for feature computation
    outcome_window_start    DATE NOT NULL,            -- Start of outcome observation period
    outcome_window_end      DATE NOT NULL,            -- End of outcome observation period
    
    -- Additional measurements
    days_past_due       INTEGER,                       -- Actual days late (0 if on time)
    label_date          DATE NOT NULL,                 -- When label was determined/computed
    
    -- Legacy compatibility
    delinquency_status  VARCHAR(20) NOT NULL,         -- Same as label_value (for backwards compatibility)
    
    -- Optional context
    notes               TEXT,                          -- Optional explanation or notes
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_label_billing FOREIGN KEY (billing_cycle_id) 
        REFERENCES billing_cycles(billing_cycle_id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_label_type CHECK (
        label_type IN ('late_30', 'late_60', 'late_90', 'default')
    ),
    CONSTRAINT chk_label_value CHECK (
        label_value IN ('on_time', '1-29_dpd', '30-59_dpd', '60-89_dpd', '90+_dpd', 'default')
    ),
    CONSTRAINT chk_delinquency_status CHECK (
        delinquency_status IN ('on_time', '1-29_dpd', '30-59_dpd', '60-89_dpd', '90+_dpd', 'default')
    ),
    CONSTRAINT chk_days_past_due CHECK (days_past_due >= 0),
    
    -- Temporal correctness constraints
    CONSTRAINT chk_outcome_window CHECK (outcome_window_end > outcome_window_start),
    CONSTRAINT chk_observation_before_outcome CHECK (outcome_window_start >= observation_date),
    
    -- Ensure label_value and delinquency_status match
    CONSTRAINT chk_label_consistency CHECK (label_value = delinquency_status)
);

-- Indexes for ML training queries
CREATE INDEX idx_label_billing ON risk_labels(billing_cycle_id);
CREATE INDEX idx_label_value ON risk_labels(label_value);
CREATE INDEX idx_label_status ON risk_labels(delinquency_status);  -- Legacy index
CREATE INDEX idx_label_date ON risk_labels(label_date);
CREATE INDEX idx_label_type ON risk_labels(label_type);
CREATE INDEX idx_label_observation ON risk_labels(observation_date);

COMMENT ON TABLE risk_labels IS 'Supervised learning targets - what we predict. CRITICAL: Features use data ≤ observation_date, labels use data > observation_date';
COMMENT ON COLUMN risk_labels.label_type IS 'Prediction task type: late_30 (30-day delinquency), late_60, late_90, or default';
COMMENT ON COLUMN risk_labels.label_value IS 'Classification target: on_time, 1-29_dpd, 30-59_dpd, 60-89_dpd, 90+_dpd, default';
COMMENT ON COLUMN risk_labels.observation_date IS 'CRITICAL: Cutoff date for features - all features must use data ≤ this date';
COMMENT ON COLUMN risk_labels.outcome_window_start IS 'Start of period where outcome is observed (typically due_date)';
COMMENT ON COLUMN risk_labels.outcome_window_end IS 'End of outcome observation period (e.g., due_date + 30 days for late_30)';
COMMENT ON COLUMN risk_labels.days_past_due IS 'Regression target option - actual delay in days';
COMMENT ON COLUMN risk_labels.delinquency_status IS 'Legacy field - same as label_value for backwards compatibility';


-- ============================================================================
-- TABLE 7: demographics
-- Description: Demographic attributes for fairness analysis ONLY
-- Granularity: One record per user
-- Temporal: Slowly changing dimensions
-- CRITICAL: Never use directly for prediction - fairness evaluation only
-- ============================================================================

CREATE TABLE demographics (
    user_id             VARCHAR(50) PRIMARY KEY,
    age_group           VARCHAR(20),              -- '18-25', '26-35', '36-50', '51-65', '65+'
    gender              VARCHAR(20),              -- For bias detection only
    income_band         VARCHAR(30),              -- 'low', 'medium', 'high', 'very_high'
    education_level     VARCHAR(30),              -- 'high_school', 'bachelors', 'masters', 'phd'
    employment_status   VARCHAR(30),              -- 'employed', 'self_employed', 'unemployed', 'student', 'retired'
    marital_status      VARCHAR(20),              -- 'single', 'married', 'divorced', 'widowed'
    region              VARCHAR(50),              -- Geographic region
    city_type           VARCHAR(20),              -- 'urban', 'suburban', 'rural'
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_demo_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexes for fairness analysis
CREATE INDEX idx_demo_age ON demographics(age_group);
CREATE INDEX idx_demo_gender ON demographics(gender);
CREATE INDEX idx_demo_income ON demographics(income_band);
CREATE INDEX idx_demo_region ON demographics(region);

COMMENT ON TABLE demographics IS 'Protected attributes - for fairness analysis ONLY, never for prediction';
COMMENT ON COLUMN demographics.age_group IS 'Binned age ranges to protect PII';
COMMENT ON COLUMN demographics.income_band IS 'Income brackets for bias detection';


-- ============================================================================
-- OPTIONAL TABLE 8: model_predictions (for production tracking)
-- Description: Store model predictions for monitoring and drift detection
-- Granularity: One record per prediction made
-- ============================================================================

CREATE TABLE model_predictions (
    prediction_id       VARCHAR(50) PRIMARY KEY,
    billing_cycle_id    VARCHAR(50) NOT NULL,
    model_version       VARCHAR(20) NOT NULL,     -- Track which model made prediction
    prediction_date     DATE NOT NULL,            -- When prediction was made
    predicted_risk      VARCHAR(20) NOT NULL,     -- Model's prediction
    risk_probability    DECIMAL(5, 4),            -- Probability score (0-1)
    confidence_score    DECIMAL(5, 4),            -- Model confidence
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_pred_billing FOREIGN KEY (billing_cycle_id) 
        REFERENCES billing_cycles(billing_cycle_id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_risk_prob CHECK (risk_probability BETWEEN 0 AND 1),
    CONSTRAINT chk_confidence CHECK (confidence_score BETWEEN 0 AND 1)
);

CREATE INDEX idx_pred_billing ON model_predictions(billing_cycle_id);
CREATE INDEX idx_pred_date ON model_predictions(prediction_date);
CREATE INDEX idx_pred_version ON model_predictions(model_version);

COMMENT ON TABLE model_predictions IS 'Production predictions - for monitoring and drift detection';


-- ============================================================================
-- OPTIONAL TABLE 9: feature_store (for pre-computed features)
-- Description: Cache computed features for performance
-- Granularity: One record per billing cycle
-- Note: These ARE derived, but cached for efficiency
-- ============================================================================

CREATE TABLE feature_store (
    feature_id          VARCHAR(50) PRIMARY KEY,
    billing_cycle_id    VARCHAR(50) NOT NULL,
    feature_version     VARCHAR(20) NOT NULL,     -- Track feature engineering version
    
    -- Utilization features (examples)
    credit_utilization  DECIMAL(5, 4),            -- total_balance / credit_limit
    
    -- Payment behavior features
    payment_delay_freq  INTEGER,                  -- # of late payments in last 6 months
    avg_payment_ratio   DECIMAL(5, 4),            -- avg(payment/total_due) over time
    
    -- Spending features
    monthly_spend       DECIMAL(10, 2),           -- spending in this cycle
    spend_volatility    DECIMAL(10, 2),           -- std dev of spending
    
    -- Temporal features
    months_since_open   INTEGER,
    days_since_last_payment INTEGER,
    
    computed_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_features_billing FOREIGN KEY (billing_cycle_id) 
        REFERENCES billing_cycles(billing_cycle_id) ON DELETE CASCADE
);

CREATE INDEX idx_features_billing ON feature_store(billing_cycle_id);
CREATE INDEX idx_features_version ON feature_store(feature_version);

COMMENT ON TABLE feature_store IS 'Pre-computed features - derived but cached for performance';
COMMENT ON COLUMN feature_store.feature_version IS 'Track feature engineering iterations';


-- ============================================================================
-- VIEWS: Useful analytical views
-- ============================================================================

-- View 1: Active cards with current utilization
CREATE VIEW v_active_cards AS
SELECT 
    c.card_id,
    c.user_id,
    c.credit_limit,
    c.card_open_date,
    CURRENT_DATE - c.card_open_date AS days_since_open
FROM credit_cards c
WHERE c.card_status = 'active';

COMMENT ON VIEW v_active_cards IS 'Quick access to active cards only';


-- View 2: Latest billing cycle per card
CREATE VIEW v_latest_billing_cycles AS
SELECT 
    bc.*,
    ROW_NUMBER() OVER (PARTITION BY bc.card_id ORDER BY bc.cycle_end_date DESC) AS rn
FROM billing_cycles bc;

COMMENT ON VIEW v_latest_billing_cycles IS 'Latest billing cycle for each card';


-- View 3: Payment summary per billing cycle
CREATE VIEW v_payment_summary AS
SELECT 
    p.billing_cycle_id,
    COUNT(*) AS num_payments,
    SUM(p.payment_amount) AS total_paid,
    MIN(p.payment_date) AS first_payment_date,
    MAX(p.payment_date) AS last_payment_date
FROM payments p
WHERE p.payment_status = 'completed'
GROUP BY p.billing_cycle_id;

COMMENT ON VIEW v_payment_summary IS 'Aggregated payment info per billing cycle';


-- ============================================================================
-- INDEXES SUMMARY
-- ============================================================================

-- Time-based indexes (critical for time-series analysis):
-- - idx_txn_date on transactions(transaction_date)
-- - idx_billing_cycle_dates on billing_cycles(cycle_start_date, cycle_end_date)
-- - idx_payment_date on payments(payment_date)

-- Relationship indexes (for joins):
-- - idx_cards_user on credit_cards(user_id)
-- - idx_txn_card on transactions(card_id)
-- - idx_billing_card on billing_cycles(card_id)
-- - idx_payment_billing on payments(billing_cycle_id)

-- Status/categorical indexes (for filtering):
-- - idx_users_status on users(account_status)
-- - idx_cards_status on credit_cards(card_status)
-- - idx_label_status on risk_labels(delinquency_status)


-- ============================================================================
-- DATA VALIDATION TRIGGERS (Optional - for data quality)
-- ============================================================================

-- Example: Prevent future transaction dates
CREATE OR REPLACE FUNCTION check_transaction_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.transaction_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Transaction date cannot be in the future';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_transaction_date
    BEFORE INSERT OR UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION check_transaction_date();


-- Example: Auto-update timestamps
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_users_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_update_cards_timestamp
    BEFORE UPDATE ON credit_cards
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();


-- ============================================================================
-- SCHEMA NOTES & DESIGN DECISIONS
-- ============================================================================

/*
1. TIME COLUMNS:
   - Every table has temporal information (dates/timestamps)
   - Critical for time-series feature engineering
   - Allows point-in-time correctness

2. NO DERIVED COLUMNS IN BASE TABLES:
   - credit_utilization NOT stored in credit_cards
   - payment_delay NOT stored in payments
   - All calculated at query time or in feature_store
   - Ensures data integrity and flexibility

3. PRIMARY KEYS:
   - All VARCHAR(50) for flexibility
   - Can use UUIDs, snowflake IDs, or custom schemes
   - Consistent across tables

4. FOREIGN KEYS:
   - ON DELETE CASCADE for referential integrity
   - Clear hierarchical relationships

5. CONSTRAINTS:
   - Check constraints for data validation
   - Prevent invalid states at database level

6. INDEXES:
   - Focused on time-series queries
   - Support for windowing operations
   - Join optimization

7. SENSITIVE DATA:
   - demographics table isolated
   - Never join to features for prediction
   - Only for fairness evaluation

8. SCALABILITY:
   - transactions table will be largest
   - Consider partitioning by transaction_date
   - feature_store for pre-computation

9. AUDIT TRAIL:
   - created_at/updated_at on most tables
   - model_predictions for production monitoring
*/

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================