"""
Fintech Risk Ops Analytics — local end-to-end demo.

Runs:
  1. KPI pipeline  (fraud / chargeback rates per region)
  2. ML model      (sklearn RandomForest fraud detector)
  3. Prints a risk summary to stdout
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "models"))

from kpi_pipeline import compute_kpis, load_transactions, write_summary  # noqa: E402


def run_kpi_pipeline() -> dict:
    input_file = ROOT / "data" / "sample_transactions.csv"
    output_file = ROOT / "analysis" / "kpi_summary.json"
    rows = load_transactions(input_file)
    summary = compute_kpis(rows)
    write_summary(summary, output_file)
    return summary


def run_fraud_model(transactions: list[dict]) -> dict:
    try:
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report
        import joblib

        df = pd.DataFrame(transactions)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["is_night"] = ((df["hour"] < 6) | (df["hour"] > 22)).astype(int)
        df["amount_log"] = np.log1p(df["amount"].astype(float))
        df["is_fraud_label"] = df["fraud_flag"].str.lower() == "true"

        feature_cols = ["amount_log", "hour", "is_night"]
        X = df[feature_cols].values
        y = df["is_fraud_label"].astype(int).values

        if y.sum() < 2:
            return {"error": "not enough fraud samples for training"}

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, class_weight="balanced")
        clf.fit(X_train, y_train)

        model_path = ROOT / "models" / "fraud_model.pkl"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(clf, model_path)

        y_pred = clf.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)

        return {
            "model_path": str(model_path),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "precision": round(report.get("1", {}).get("precision", 0), 4),
            "recall": round(report.get("1", {}).get("recall", 0), 4),
            "f1_score": round(report.get("1", {}).get("f1-score", 0), 4),
        }
    except ImportError as exc:
        return {"error": f"Missing dependency: {exc}. Run: pip install scikit-learn joblib pandas numpy"}


if __name__ == "__main__":
    print("=" * 60)
    print("Fintech Risk Ops Analytics — Local Demo")
    print("=" * 60)

    # Step 1: KPI pipeline
    print("\n[1/2] Running KPI pipeline …")
    kpis = run_kpi_pipeline()
    print(f"  Total transactions : {kpis['total_transactions']}")
    print(f"  Success rate       : {kpis['transaction_success_rate']:.1%}")
    print(f"  Fraud rate         : {kpis['fraud_rate']:.1%}")
    print(f"  Chargeback rate    : {kpis['chargeback_rate']:.1%}")

    top_region = max(kpis["regional_breakdown"], key=lambda r: kpis["regional_breakdown"][r]["fraud"])
    print(f"  Highest fraud region: {top_region}")

    # Step 2: ML fraud model
    print("\n[2/2] Training fraud detection model …")
    input_file = ROOT / "data" / "sample_transactions.csv"
    import csv
    with input_file.open(encoding="utf-8") as f:
        transactions = list(csv.DictReader(f))

    model_result = run_fraud_model(transactions)
    if "error" in model_result:
        print(f"  Warning: {model_result['error']}")
    else:
        print(f"  Trained on {model_result['train_samples']} samples")
        print(f"  Precision: {model_result['precision']:.1%}  Recall: {model_result['recall']:.1%}  F1: {model_result['f1_score']:.1%}")
        print(f"  Model saved -> {model_result['model_path']}")

    # Output combined summary
    output = {"kpi_summary": kpis, "model_metrics": model_result}
    summary_path = ROOT / "analysis" / "kpi_summary.json"
    print(f"\n  Full KPI summary -> {summary_path}")

    print("\n  To launch the Streamlit risk dashboard:")
    print("    streamlit run dashboards/risk_dashboard.py")

    print("\n  To start the fraud detection API:")
    print("    uvicorn services.api:app --reload\n")
