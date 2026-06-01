import json
from pathlib import Path

from kpi_pipeline import compute_kpis, load_transactions, write_summary


def run_demo() -> dict:
    root = Path(__file__).resolve().parents[1]
    input_file = root / "data" / "sample_transactions.csv"
    output_file = root / "analysis" / "kpi_summary.json"

    transactions = load_transactions(input_file)
    summary = compute_kpis(transactions)
    write_summary(summary, output_file)

    return {
        "transactions": summary.get("total_transactions", 0),
        "success_rate": summary.get("transaction_success_rate", 0),
        "fraud_rate": summary.get("fraud_rate", 0),
        "summary_output": str(output_file),
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
