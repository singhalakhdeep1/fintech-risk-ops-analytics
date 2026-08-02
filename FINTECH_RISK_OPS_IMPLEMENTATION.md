# Fintech Risk Ops Analytics - Implementation

## Overview
This document describes the data engineering and data quality integrations added to Fintech Risk Ops Analytics.

## Technologies Added

### 1. Apache Airflow
- DAG for risk pipeline
- Task orchestration
- Scheduled execution
- Retry logic
- Email notifications

### 2. dbt Cloud
- Risk metrics model
- Risk alerts model
- SQL transformations
- Data warehouse integration

### 3. Monte Carlo
- Data quality monitoring
- Custom metrics
- Risk score distribution monitoring
- Null value detection
- Outlier detection

### 4. Great Expectations
- Expectation suite creation
- Risk data validation
- Column expectations
- Row count validation
- Uniqueness checks

### 5. Prefect
- Risk analysis flow
- Task orchestration
- Anomaly detection
- Report generation
- Alert sending

## Files Created

### Airflow
- `ops/airflow/dags/risk_pipeline.py` - Airflow DAG for risk pipeline

### dbt
- `ops/dbt/models/risk_metrics.sql` - Risk metrics model
- `ops/dbt/models/risk_alerts.sql` - Risk alerts model

### Monte Carlo
- `ops/monte_carlo/monitoring/risk_data_quality.py` - Data quality monitoring

### Great Expectations
- `ops/great_expectations/risk_expectations.py` - Risk data expectations

### Prefect
- `ops/prefect/flows/risk_analysis_flow.py` - Risk analysis flow

## Features

### Airflow DAG
- Extract risk data from source systems
- Transform and enrich risk data
- Load to data warehouse
- Run risk scoring models
- Generate risk reports
- Daily schedule at 2 AM
- Retry logic with 2 retries
- Email on failure

### dbt Models
- Risk metrics with daily aggregation
- Transaction type breakdown
- Risk score statistics (avg, max)
- High risk count and percentage
- Risk alerts based on 95th percentile
- Alert type and message generation

### Monte Carlo Monitoring
- Custom metric creation
- Risk score distribution monitoring (p25, p50, p75, p95)
- Null risk score detection
- Outlier detection using IQR method
- Daily schedule for metrics
- Data quality reports

### Great Expectations
- Column existence checks
- Risk score range validation (0-1)
- Null value checks
- Amount range validation
- Transaction type validation
- Row count validation
- Unique transaction ID check

### Prefect Flow
- Extract risk transactions task
- Calculate risk scores task
- Detect anomalies task
- Generate risk report task
- Send alerts task
- Scheduled execution
- Logging support

## Installation Required

Add to `requirements.txt`:
```txt
apache-airflow
dbt-core
monte-carlo
great-expectations
prefect
```

Run:
```bash
pip install -r requirements.txt
```

## Environment Variables

```env
# Monte Carlo
MONTE_CARLO_API_KEY=your-api-key
MONTE_CARLO_ACCOUNT_ID=your-account-id

# Airflow
AIRFLOW_HOME=/path/to/airflow
AIRFLOW__CORE__DAGS_FOLDER=/path/to/dags

# dbt
DBT_PROFILES_DIR=/path/to/profiles

# Prefect
PREFECT_API_URL=http://localhost:4200
```

## Notes
- All code is written but packages are not installed (per user request)
- Airflow requires Airflow server setup
- dbt requires dbt Cloud or dbt Core setup
- Monte Carlo requires Monte Carlo account
- Great Expectations requires GE setup
- Prefect requires Prefect server or Prefect Cloud
- All tools support scheduled execution
