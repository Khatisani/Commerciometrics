"""
Module: test_feature_export.py
Description: Unit tests for exporting the customer feature store table to a compressed Parquet file.
"""

import os
import duckdb
from scripts.export_features import export_customer_features

def test_export_customer_features(tmp_path):
    """
    Test that customer feature store table exports correctly to a compressed parquet file.
    """

    db_file = str(tmp_path / "test_export.duckdb")
    parquet_out = tmp_path / "customer_features.parquet"
    
    conn = duckdb.connect(db_file)
    conn.execute("""
        CREATE TABLE customer_feature_matrix AS SELECT * FROM (
            VALUES 
                ('Cust_A', 10, 2, 40.0, 10, 5.0, 2.0, 2, 0),
                ('Cust_B', 30, 1, 25.0, 0, 0.0, 0.0, 3, 1)
        ) AS t(CustomerID, recency_days, frequency, monetary_value, tenure_days, avg_latency_days, latency_variance, unique_stock_codes, is_churned);
    """)
    conn.close()

    df_exported = export_customer_features(db_path=db_file, output_parquet_path=str(parquet_out))
    
    assert os.path.exists(parquet_out)
    assert len(df_exported) == 2
    assert 'is_churned' in df_exported.columns
    
    conn_verify = duckdb.connect()
    df_verify = conn_verify.execute(f"SELECT * FROM read_parquet('{parquet_out}')").fetchdf()
    conn_verify.close()
    
    assert len(df_verify) == 2
    assert 'Cust_A' in df_verify['CustomerID'].values