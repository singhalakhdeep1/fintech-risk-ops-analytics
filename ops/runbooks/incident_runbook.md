# Incident Runbook - Fintech Risk and Ops Analytics

## Triggers

- Fraud rate spike alert
- Payment success rate drop alert
- KPI pipeline failures

## Immediate Steps

1. Confirm impacted regions and transaction windows.
2. Validate KPI pipeline input and aggregation jobs.
3. Escalate to risk and payments operations teams.
4. Freeze non-critical dashboard updates during investigation.

## Recovery Steps

1. Restore KPI pipeline execution and data integrity.
2. Run `analysis/run_local_demo.py` to validate baseline processing.
3. Verify updated `kpi_summary.json` reflects expected metrics.

## Post-Incident

1. Publish incident timeline and affected metrics.
2. Add regression tests for failed calculation branch.
3. Tighten fraud and payment-success monitoring thresholds.
