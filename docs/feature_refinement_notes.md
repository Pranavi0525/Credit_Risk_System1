# Feature Refinement — Week 5 Day 1

## Motivation
Baseline models showed weak generalization.
We hypothesize that interaction features better capture financial stress.

## New Features Added
- payment_stress = min_due_ratio × credit_utilization
- spend_to_limit = monthly_spend / utilization

## Observations
- payment_stress shows higher mean for late payers
- spend_to_limit shows / does not show separation

## Decision
Features that demonstrate clear behavioral meaning
and signal separation will be retained for Week 5 modeling.
