# Model Comparison — Week 5 Day 3

## Models Evaluated

The following supervised learning models were trained and evaluated for the
credit risk prediction task (late_30 delinquency):

- Logistic Regression (baseline linear model)
- Decision Tree (depth-limited, controlled complexity)
- Random Forest (controlled ensemble)

All models were evaluated using a **time-based validation split** to preserve
temporal correctness and avoid data leakage.

---

## Validation Performance (ROC-AUC)

| Model               | Validation ROC-AUC |
|--------------------|-------------------|
| Logistic Regression | **0.5486** |
| Decision Tree       | **0.8333** |
| Random Forest       | **0.3750** |

Metric used:
- **ROC-AUC** — measures how well the model ranks risky users above non-risky users,
  independent of classification threshold.

---

## Observations

1. **Logistic Regression**
   - Provides a stable but modest baseline.
   - Captures linear relationships such as:
     - credit utilization
     - rolling utilization trends
     - minimum due ratio
   - Limited ability to model non-linear credit behavior.

2. **Decision Tree**
   - Achieves the **highest validation ROC-AUC (0.83)**.
   - Indicates strong **non-linear relationships** in credit behavior.
   - Able to capture interaction effects such as:
     - spending trends combined with utilization spikes
   - However, single trees are known to be:
     - sensitive to data noise
     - less stable across time

3. **Random Forest**
   - Underperforms in validation despite being an ensemble.
   - Indicates:
     - limited data volume
     - high variance due to synthetic data
     - insufficient signal consistency across trees
   - Suggests that ensembling does **not yet improve generalization** in this setup.

4. **Feature Consistency**
   - Core risk drivers remain consistent across models:
     - rolling utilization
     - spending trends
     - payment burden indicators
   - Confirms that feature engineering is directionally correct.

---

## Decision

**Decision Tree is selected as the strongest candidate model at this stage**
based on:

- Highest validation ROC-AUC
- Ability to capture non-linear credit behavior
- Clear alignment with observed financial patterns

However:

- Logistic Regression remains valuable as a **benchmark and interpretability reference**
- Random Forest will require:
  - more data
  - stronger regularization
  - or longer time horizons to outperform simpler models

The selected model will be carried forward for:
- threshold analysis
- business cost evaluation
- fairness and stability checks
