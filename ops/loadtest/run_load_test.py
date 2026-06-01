import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.kpi_pipeline import compute_kpis


def run() -> dict:
    rows = [
        {"status": "succeeded", "fraud_flag": "false", "chargeback_flag": "false", "region": "IN"},
        {"status": "failed", "fraud_flag": "true", "chargeback_flag": "false", "region": "IN"},
        {"status": "succeeded", "fraud_flag": "false", "chargeback_flag": "true", "region": "US"},
    ]

    iterations = 20000
    started = time.perf_counter()
    for _ in range(iterations):
        compute_kpis(rows)
    duration = max(0.001, time.perf_counter() - started)

    return {
        "workload": "kpi_compute",
        "iterations": iterations,
        "rows_per_iteration": len(rows),
        "duration_sec": round(duration, 2),
        "kpi_runs_per_sec": round(iterations / duration, 2),
    }


if __name__ == "__main__":
    report = run()
    output = Path(__file__).resolve().parent / "loadtest_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
