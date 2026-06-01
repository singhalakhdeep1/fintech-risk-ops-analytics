import unittest

from kpi_pipeline import compute_kpis


class KpiPipelineTests(unittest.TestCase):
    def test_compute_kpis_returns_regional_breakdown(self) -> None:
        rows = [
            {
                "status": "succeeded",
                "fraud_flag": "false",
                "chargeback_flag": "false",
                "region": "IN",
            },
            {
                "status": "failed",
                "fraud_flag": "true",
                "chargeback_flag": "false",
                "region": "IN",
            },
            {
                "status": "succeeded",
                "fraud_flag": "false",
                "chargeback_flag": "true",
                "region": "US",
            },
        ]

        summary = compute_kpis(rows)

        self.assertEqual(summary["total_transactions"], 3)
        self.assertAlmostEqual(summary["transaction_success_rate"], 0.6667, places=4)
        self.assertAlmostEqual(summary["failure_rate"], 0.3333, places=4)
        self.assertAlmostEqual(summary["fraud_rate"], 0.3333, places=4)
        self.assertAlmostEqual(summary["chargeback_rate"], 0.3333, places=4)
        self.assertEqual(summary["regional_breakdown"]["IN"]["total"], 2)
        self.assertEqual(summary["regional_breakdown"]["US"]["chargebacks"], 1)


if __name__ == "__main__":
    unittest.main()
