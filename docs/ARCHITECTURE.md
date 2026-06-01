# Architecture — Fintech Risk Ops Analytics

## Overview

The Fintech Risk Ops Analytics platform is a KPI pipeline that reads synthetic transaction data, computes business-critical risk metrics (success rate, fraud rate, chargeback rate, regional breakdown), and writes an aggregated summary. It is designed to run as a scheduled batch job or on-demand analytics worker.

## Component Diagram

```mermaid
flowchart TD
    subgraph Source["Input Data"]
        CSV["data/transactions.csv\n(synthetic: 1000 rows\nfields: tx_id, amount, status,\nfraud_flag, chargeback_flag, region)"]
    end

    subgraph Pipeline["KPI Pipeline"]
        LT["analysis/kpi_pipeline.py\nload_transactions()  — csv.DictReader\ncompute_kpis()  — aggregate metrics\nwrite_summary()  — JSON output"]
    end

    subgraph Output["Output"]
        KPI["analysis/kpi_summary.json\n- transaction_success_rate\n- failure_rate\n- fraud_rate\n- chargeback_rate\n- total_transactions\n- regional_breakdown"]
    end

    subgraph Ops["Ops / CI"]
        LoadTest["ops/loadtest/run_load_test.py\nthroughput bench: 20 000 iterations\nSLO: ≥ 5 000 kpi_runs/sec"]
        SLO["ops/perf/validate_slo.py"]
        Alerts["ops/alerts/alert_rules.yaml"]
        DepScan["ops/security/dependency_scan.py\n(confirms stdlib-only)"]
    end

    subgraph K8s["Kubernetes"]
        Staging["staging worker  2 replicas"]
        Prod["prod worker  3 replicas"]
        Canary["canary  1 replica"]
    end

    CSV --> LT
    LT --> KPI
    LT -.->|"perf bench"| LoadTest
    LoadTest --> SLO
    Pipeline --> Staging & Prod & Canary
```

## Data Flow

1. **Load** — `load_transactions()` reads `data/transactions.csv` via `csv.DictReader` into a list of dicts
2. **Compute** — `compute_kpis()` calculates:
   - `transaction_success_rate` = succeeded / total
   - `failure_rate` = failed / total
   - `fraud_rate` = fraud_flagged / total
   - `chargeback_rate` = chargeback_flagged / total
   - `regional_breakdown` = per-region counts for all four metrics
3. **Write** — `write_summary()` writes the KPI dict as pretty-printed JSON
4. **SLO gate** — Throughput benchmark ensures `compute_kpis()` sustains ≥ 5 000 runs/sec in CI

## KPI Schema

```json
{
  "transaction_success_rate": 0.8812,
  "failure_rate": 0.1188,
  "fraud_rate": 0.0432,
  "chargeback_rate": 0.0218,
  "total_transactions": 1000,
  "regional_breakdown": {
    "IN": {
      "total": 312,
      "succeeded": 278,
      "failed": 34,
      "fraud": 14,
      "chargebacks": 7
    },
    "US": {
      "total": 688,
      "succeeded": 603,
      "failed": 85,
      "fraud": 29,
      "chargebacks": 15
    }
  }
}
```

## Key Design Decisions

| Decision                  | Rationale                                                                    |
| ------------------------- | ---------------------------------------------------------------------------- |
| CSV input                 | Common format for transaction data exports; easy to swap for a real DB query |
| `defaultdict` for regions | Automatically handles new region codes without schema migration              |
| Stdlib-only               | Zero dependencies — runs in any Python 3.12 environment without pip install  |
| Synthetic data            | No real cardholder data in repo; PCI-DSS compliant by design                 |
| Throughput SLO            | `compute_kpis()` is a hot path — regressions caught before merge             |

## Regulatory Considerations (Production)

| Regulation | Requirement                                       | Status                          |
| ---------- | ------------------------------------------------- | ------------------------------- |
| PCI-DSS    | Tokenise PANs before pipeline entry               | Demo: synthetic data only       |
| SOC 2      | Log all data access with actor + timestamp        | Production integration needed   |
| GDPR/CCPA  | Right-to-erasure for customer-linked transactions | Not applicable (synthetic data) |

## Production Architecture (Target)

```mermaid
flowchart LR
    TxnDB["Transaction DB\n(PostgreSQL / Aurora)"] -->|"daily export"| S3["S3 / GCS\n(encrypted, KMS)"]
    S3 --> Spark["Apache Spark\n(distributed KPI compute)"]
    Spark --> Warehouse["Snowflake / Redshift\n(risk_kpi table)"]
    Warehouse --> Dashboard["Grafana / Tableau\n(fraud ops dashboard)"]
    Warehouse --> Alerting["PagerDuty\n(fraud_rate > threshold)"]
```

## Directory Map

```
fintech-risk-ops-analytics/
├── analysis/
│   ├── kpi_pipeline.py          # load / compute / write
│   ├── run_local_demo.py        # end-to-end demo
│   ├── test_kpi_pipeline.py     # unittest
│   └── kpi_summary.json         # output (gitignored)
├── data/
│   └── transactions.csv         # synthetic transaction data
├── deploy/k8s/
│   ├── staging/ prod/ canary/
├── ops/
│   ├── alerts/ loadtest/ perf/ runbooks/ security/
└── .github/workflows/ci.yml
```
