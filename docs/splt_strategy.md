# Train/Validation Split Strategy

## Rationale
Credit risk is a time-dependent problem.
Random splits can leak future behavior into training.

## Method
- Prediction unit: billing cycle
- Split criterion: cycle_end_date
- Training set: earliest 75% of cycles
- Validation set: latest 25% of cycles

## Integrity Checks
- No overlap in time between train and validation
- Labels observed strictly after observation window
- Feature computation frozen before split

## Benefit
This split simulates real-world deployment,
where models trained on past data predict future risk.
