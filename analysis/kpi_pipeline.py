import csv
import json
from collections import defaultdict
from pathlib import Path


def load_transactions(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def compute_kpis(rows: list[dict]) -> dict:
    total = len(rows)
    if total == 0:
        return {}

    succeeded = [row for row in rows if row["status"] == "succeeded"]
    failed = [row for row in rows if row["status"] == "failed"]
    fraud = [row for row in rows if row["fraud_flag"].lower() == "true"]
    chargebacks = [row for row in rows if row["chargeback_flag"].lower() == "true"]

    by_region = defaultdict(lambda: {"total": 0, "succeeded": 0, "failed": 0, "fraud": 0, "chargebacks": 0})
    for row in rows:
        region = row["region"]
        bucket = by_region[region]
        bucket["total"] += 1
        if row["status"] == "succeeded":
            bucket["succeeded"] += 1
        if row["status"] == "failed":
            bucket["failed"] += 1
        if row["fraud_flag"].lower() == "true":
            bucket["fraud"] += 1
        if row["chargeback_flag"].lower() == "true":
            bucket["chargebacks"] += 1

    return {
        "transaction_success_rate": round(len(succeeded) / total, 4),
        "failure_rate": round(len(failed) / total, 4),
        "fraud_rate": round(len(fraud) / total, 4),
        "chargeback_rate": round(len(chargebacks) / total, 4),
        "total_transactions": total,
        "regional_breakdown": dict(by_region),
    }


def write_summary(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    input_file = root / "data" / "sample_transactions.csv"
    output_file = root / "analysis" / "kpi_summary.json"
    transactions = load_transactions(input_file)
    kpi_summary = compute_kpis(transactions)
    write_summary(kpi_summary, output_file)
    print(json.dumps(kpi_summary, indent=2))
