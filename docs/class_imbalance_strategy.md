# Class Imbalance Strategy — Week 5 Day 2

## Problem
Late payment is a minority outcome (~20%).
Standard models bias toward majority class.

## Strategies Evaluated
1. Baseline logistic regression
2. Logistic regression with class_weight="balanced"
3. Decision threshold tuning

## Observations
- Class weighting improved / degraded ROC-AUC
- Lower thresholds increase recall at the cost of false positives

## Decision
We prefer class weighting and threshold tuning
over resampling to preserve temporal realism
and regulatory acceptability.
