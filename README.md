# Fintech Risk and Operations Analytics

Operational analytics platform for payments, fraud, KYC, disputes, and settlement performance.

## Stack

- Data processing: SQL + Python
- Warehouse: PostgreSQL or ClickHouse
- Transform: dbt
- BI: Power BI, Tableau, or Metabase
- Scheduling: Airflow

## KPI areas

- Payment success rate
- Fraud rate
- Chargeback rate
- KYC completion rate
- Settlement time
- Dispute resolution SLA

## First build milestone

1. Generate realistic payments, KYC, and chargeback datasets
2. Build marts for payments health and fraud operations
3. Create dashboards for risk, operations, and executive reporting
4. Add anomaly alerts for transaction success and fraud spikes

## Implemented baseline

- Seed transaction dataset covering status, fraud, and chargebacks
- KPI pipeline script producing operational summary JSON
- SQL model draft for payment health regional mart
- Dashboard plan mapped to payment, fraud, chargeback, and KYC operations
- Unit test coverage for KPI math and regional aggregation

## Run KPI pipeline

```bash
cd analysis
python kpi_pipeline.py
```

## One-command local demo

```bash
cd analysis
python run_local_demo.py
```

Output file:

- `analysis/kpi_summary.json`

## Validate

```bash
cd analysis
python -m unittest discover -s . -p "test_*.py"
```
