# Monte Carlo data quality monitoring for fintech-risk-ops-analytics

import os
from montecarlo import MCClient

class MonteCarloQualityMonitor:
    def __init__(self):
        self.client = MCClient(
            api_key=os.getenv('MONTE_CARLO_API_KEY'),
            account_id=os.getenv('MONTE_CARLO_ACCOUNT_ID')
        )

    def create_custom_metric(self, metric_config):
        """Create a custom data quality metric"""
        return self.client.create_custom_metric(metric_config)

    def run_data_quality_check(self, table_name, check_type):
        """Run data quality check on a table"""
        return self.client.run_table_quality_check(
            table_name=table_name,
            check_type=check_type
        )

    def get_data_quality_report(self, table_name, date_range):
        """Get data quality report for a table"""
        return self.client.get_table_quality_report(
            table_name=table_name,
            start_date=date_range['start'],
            end_date=date_range['end']
        )

    def monitor_risk_score_distribution(self, table_name, column_name):
        """Monitor risk score distribution"""
        metric_config = {
            'name': 'risk_score_distribution',
            'description': 'Monitor distribution of risk scores',
            'query': f'''
                SELECT
                    percentile_cont(0.25) as p25,
                    percentile_cont(0.50) as p50,
                    percentile_cont(0.75) as p75,
                    percentile_cont(0.95) as p95,
                    avg({column_name}) as avg,
                    stddev({column_name}) as stddev
                FROM {table_name}
            ''',
            'schedule': 'daily'
        }
        return self.create_custom_metric(metric_config)

    def monitor_null_risk_scores(self, table_name, column_name):
        """Monitor for null risk scores"""
        metric_config = {
            'name': 'null_risk_scores',
            'description': 'Monitor for null risk scores',
            'query': f'''
                SELECT
                    COUNT(*) as total_rows,
                    SUM(CASE WHEN {column_name} IS NULL THEN 1 ELSE 0 END) as null_count,
                    (SUM(CASE WHEN {column_name} IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as null_percentage
                FROM {table_name}
            ''',
            'schedule': 'daily'
        }
        return self.create_custom_metric(metric_config)

    def monitor_risk_score_outliers(self, table_name, column_name):
        """Monitor for risk score outliers"""
        metric_config = {
            'name': 'risk_score_outliers',
            'description': 'Monitor for risk score outliers using IQR method',
            'query': f'''
                WITH stats AS (
                    SELECT
                        percentile_cont(0.25) as q1,
                        percentile_cont(0.75) as q3
                    FROM {table_name}
                ),
                bounds AS (
                    SELECT
                        q1,
                        q3,
                        q3 - 1.5 * (q3 - q1) as lower_bound,
                        q3 + 1.5 * (q3 - q1) as upper_bound
                    FROM stats
                )
                SELECT
                    COUNT(*) as total_rows,
                    SUM(CASE WHEN {column_name} < lower_bound OR {column_name} > upper_bound THEN 1 ELSE 0 END) as outlier_count
                FROM {table_name}, bounds
            ''',
            'schedule': 'daily'
        }
        return self.create_custom_metric(metric_config)

# Example usage
if __name__ == '__main__':
    monitor = MonteCarloQualityMonitor()
    monitor.monitor_risk_score_distribution('risk_transactions', 'risk_score')
    monitor.monitor_null_risk_scores('risk_transactions', 'risk_score')
    monitor.monitor_risk_score_outliers('risk_transactions', 'risk_score')
