"""
Module: test_feature_store_integration.py
Description: End-to-end integration tests validating the final feature store schema, row counts, and null checks.
"""
import os
import duckdb

FEATURE_STORE_PATH = "data/processed/customer_features.parquet"

def test_feature_store_integration():
    """
    End-to-end integration test for the final customer feature store parquet file.
    """

    assert os.path.exists(FEATURE_STORE_PATH), f"Feature store parquet file not found at {FEATURE_STORE_PATH}."
    
    conn = duckdb.connect()
    df = conn.execute(f"SELECT * FROM read_parquet('{FEATURE_STORE_PATH}')").fetchdf()
    conn.close()

    assert len(df) > 0, "Feature store is empty (0 rows)."

    expected_columns = [
        'CustomerID',
        'recency_days',
        'frequency',
        'monetary_value',
        'tenure_days',
        'avg_latency_days',
        'latency_variance',
        'unique_stock_codes',
        'is_churned'
    ]
    for col in expected_columns:
        assert col in df.columns, f"Required feature column '{col}' is missing from the feature store schema."
        
    assert df['CustomerID'].isnull().sum() == 0, "CustomerID contains null values."
    assert df['is_churned'].isnull().sum() == 0, "Target variable 'is_churned' contains null values."
    assert df['recency_days'].isnull().sum() == 0, "Feature 'recency_days' contains null values."
    assert df['frequency'].isnull().sum() == 0, "Feature 'frequency' contains null values."
    assert df['monetary_value'].isnull().sum() == 0, "Feature 'monetary_value' contains null values."
    assert df['tenure_days'].isnull().sum() == 0, "Feature 'tenure_days' contains null values."