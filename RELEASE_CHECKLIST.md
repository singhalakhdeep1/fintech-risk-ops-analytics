# Fintech Risk and Ops Analytics - Release Checklist

Release status: Production-demo ready
Last updated: 2026-06-01

## Acceptance Criteria

- [x] KPI pipeline implemented: `analysis/kpi_pipeline.py`
- [x] Regional payment-health SQL model included: `models/payment_health.sql`
- [x] One-command demo run works: `python analysis/run_local_demo.py`
- [x] KPI artifact is generated: `analysis/kpi_summary.json`
- [x] Unit tests pass: `python -m unittest discover -s analysis -p "test_*.py"`
- [x] KPI areas covered: success rate, failure rate, fraud rate, chargeback rate, regional breakdown
- [x] CI workflow exists and runs demo + tests: `.github/workflows/ci.yml`

## Production-Demo Sign-Off

- [x] Ready for recruiter demo
- [x] Ready for portfolio showcase
- [x] Ready for interview walk-through

## Notes

This release focuses on operational KPI clarity and deterministic outputs for demo and interview scenarios.
