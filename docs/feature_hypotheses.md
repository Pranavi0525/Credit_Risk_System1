# Feature Hypotheses for Credit Risk Modeling

## Core Level Features
- Credit utilization (higher → higher risk)
- Minimum due ratio (higher → liquidity stress)

## Behavioral Features
- Monthly spend (extremes may indicate stress or affluence)
- Spend volatility (higher → unstable cash flow)
- Category concentration (higher → dependency risk)

## Temporal Features
- Utilization trend (positive slope → increasing risk)
- Spend shocks (sudden spikes → early warning)
- Rolling averages (smooth noise, capture momentum)

## Interaction Hypotheses
- High utilization + high volatility → highest risk
- Rising utilization + spend shocks → early delinquency
- Low utilization + stable spend → lowest risk
