# Security Policy — Fintech Risk Ops Analytics

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.x     | ✅ Yes    |
| < 1.0   | ❌ No     |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report security issues to: **security@alakhdeepsingh.dev**

Include in your report:

- Description of the vulnerability and its impact
- Steps to reproduce or proof-of-concept
- Affected component (KPI pipeline, transaction data, fraud detection, CI pipeline)
- Suggested remediation if known

We acknowledge reports within **48 hours** and aim to provide a resolution timeline within **7 days**.

## Security Controls

### Dependency Management

- This project uses Python 3.12 standard library only (zero third-party runtime dependencies)
- `ops/security/dependency_scan.py` runs on every CI push — confirms stdlib-only posture
- SBOM is maintained at `ops/security/sbom.txt` (SPDX 2.3 format)

### Transaction Data Security

- **Sample data only**: `data/transactions.csv` contains fully synthetic data — no real cardholder or merchant information
- In production, transaction CSVs must be encrypted at rest (AES-256) and access-controlled via IAM
- Fraud flags and chargeback flags are read-only inputs to the KPI pipeline — never written back to source systems

### KPI Output Security

- `kpi_summary.json` output contains only aggregate statistics — no individual transaction data
- The summary file is excluded from version control (`.gitignore`)
- Regional breakdown data does not include individual merchant or customer identifiers

### Regulatory Compliance Notes (Production)

- PCI-DSS: Cardholder data must be tokenized before entering analytics pipelines
- SOC 2 Type II: All data access must be logged with user identity and timestamp
- GDPR/CCPA: Implement a right-to-erasure pipeline for any customer-linked analytics data

### Container Security

- Worker images are built from `python:3.12-slim`
- No credentials or PII baked into images

### Kubernetes Security

- Worker pods run as non-root (`runAsNonRoot: true`)
- Resource limits prevent pipeline jobs from exhausting cluster resources

## Known Limitations (Demo Scope)

This project uses synthetic CSV data and local file output. In a production deployment:

- Replace with encrypted S3/GCS input data with KMS key rotation
- Add data lineage tracking (OpenLineage / Marquez)
- Integrate fraud signal enrichment with a real-time feature store

## Security Changelog

| Date       | Change                                        |
| ---------- | --------------------------------------------- |
| 2025-06-01 | Initial security policy published             |
| 2025-06-01 | Dependency scan and SBOM added to CI pipeline |
