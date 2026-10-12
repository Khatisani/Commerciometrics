"""
Module: test_feature_matrix_join.py
Description: Unit tests for joining customer features and 90-day churn target labels into a master feature matrix.
"""

import os
import pytest
import duckdb
from scripts.build_feature_matrix import build_customer_feature_matrix

def test_build_customer_feature_matrix(tmp_path):
    """
    Test that RFM, behavioral, and target tables successfully join into a master feature matrix.
    """
    
    db_file = str(tmp_path / "test_matrix.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute("""
        CREATE TABLE customer_rfm AS SELECT * FROM (
            VALUES ('Cust_A', '2010-12-21', 10, 2, 40.0), ('Cust_B', '2010-12-01', 30, 1, 25.0)
        ) AS t(CustomerID, last_purchase_date, recency_days, frequency, monetary_value);
        
        CREATE TABLE customer_behavioral AS SELECT * FROM (
            VALUES ('Cust_A', '2010-12-01', '2010-12-11', 10, 5.0, 2.0, 2), ('Cust_B', '2010-12-05', '2010-12-05', 0, 0.0, 0.0, 3)
        ) AS t(CustomerID, first_purchase_date, last_purchase_date, tenure_days, avg_latency_days, latency_variance, unique_stock_codes);
        
        CREATE TABLE feature_target AS SELECT * FROM (
            VALUES ('Cust_A', '2010-12-21', 10, 0), ('Cust_B', '2010-12-01', 30, 1)
        ) AS t(CustomerID, last_purchase_date, recency_days, is_churned);
    """)
    conn.close()
    
    df_matrix = build_customer_feature_matrix(db_path=db_file)
    
    assert len(df_matrix) == 2
    assert 'is_churned' in df_matrix.columns
    assert 'recency_days' in df_matrix.columns
    assert 'tenure_days' in df_matrix.columns
    assert 'frequency' in df_matrix.columns
    assert 'monetary_value' in df_matrix.columns
    
    cust_a = df_matrix[df_matrix['CustomerID'] == 'Cust_A'].iloc[0]
    cust_b = df_matrix[df_matrix['CustomerID'] == 'Cust_B'].iloc[0]
    
    assert int(cust_a['is_churned']) == 0
    assert int(cust_b['is_churned']) == 1