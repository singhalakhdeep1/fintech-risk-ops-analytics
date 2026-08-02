# Great Expectations for fintech-risk-ops-analytics

import great_expectations as gx
from great_expectations.core import ExpectationSuite, ExpectationConfiguration

class RiskDataExpectations:
    def __init__(self):
        self.context = gx.get_context()

    def create_risk_suite(self):
        """Create expectation suite for risk data"""
        suite = ExpectationSuite(
            expectation_suite_name="risk_data_expectations"
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_to_exist",
                kwargs={"column": "transaction_id"}
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_to_exist",
                kwargs={"column": "risk_score"}
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={
                    "column": "risk_score",
                    "min_value": 0,
                    "max_value": 1
                }
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_not_be_null",
                kwargs={"column": "risk_score"}
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={
                    "column": "amount",
                    "min_value": 0,
                    "max_value": 1000000
                }
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_in_set",
                kwargs={
                    "column": "transaction_type",
                    "value_set": ["payment", "transfer", "withdrawal", "deposit"]
                }
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_table_row_count_to_be_between",
                kwargs={"min_value": 1, "max_value": 1000000}
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_unique",
                kwargs={"column": "transaction_id"}
            )
        )

        return suite

    def validate_risk_data(self, df):
        """Validate risk data against expectations"""
        suite = self.create_risk_suite()
        batch = gx.dataset.PandasDataset(df)
        results = batch.validate(suite)
        return results

    def save_suite(self):
        """Save expectation suite to Great Expectations"""
        suite = self.create_risk_suite()
        self.context.add_expectation_suite(suite)
        return suite

# Example usage
if __name__ == '__main__':
    expectations = RiskDataExpectations()
    expectations.save_suite()
