Baseline Model Results — Week 4 Day 4
Target
late_30 (30+ days past due)

Models
Logistic Regression: A linear baseline providing high interpretability; used to establish the strength of direct relationships between features and risk.

Decision Tree (depth=4): A non-linear baseline used to capture complex interactions and "if-then" rules in borrower behavior.

Performance (ROC-AUC)
Logistic Regression

Train: 0.580

Validation: 0.451

Decision Tree

Train: 0.589

Validation: 0.354

Key Signals
Strong risk drivers:

util_roll_3: Positively correlated with risk (0.121); indicates sustained high credit usage is a primary danger signal.

credit_utilization: A strong linear driver (0.110); higher current utilization directly increases the probability of delinquency.

Protective factors:

min_due_ratio: The strongest protective signal (-0.290); paying more than the minimum required suggests financial stability.

spend_shock: Negatively correlated (-0.189); in this specific baseline, sudden spending increases appear inversely related to immediate risk.

Overfitting Assessment
Logistic Regression: Moderate. The drop from 0.58 to 0.45 suggests the linear signals captured in training are losing predictive power on the future validation set.

Decision Tree: High. With a validation score of 0.35 (worse than random guessing) compared to a 0.59 training score, the tree is heavily "memorizing" noise.

Conclusion
Baseline models confirm the presence of behavioral risk signals, particularly around utilization trends and payment ratios. While the Logistic Regression provides a more stable foundation, the significant performance drop in validation indicates that simple models are struggling with the time-based shift in data. The Decision Tree's extreme reliance on spend_roll_3 (1.0 importance) highlights a need for better tree pruning or class balancing in the next phase.