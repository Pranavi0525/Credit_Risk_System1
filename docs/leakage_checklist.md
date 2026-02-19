# Target Leakage Prevention Checklist

## Temporal Boundaries
- [x] Observation cutoff defined per billing cycle
- [x] Features use data ≤ cycle_end_date
- [x] Labels defined after due_date

## Feature Engineering
- [x] No future transactions used
- [x] Rolling features use backward windows only
- [x] No label-derived features included

## Data Sources
- [x] Demographics excluded from prediction
- [x] Payments not used before label creation
- [x] Synthetic data generation respects timelines

## Validation
- [x] Manual inspection of time ordering
- [x] Explicit leakage examples identified and excluded
