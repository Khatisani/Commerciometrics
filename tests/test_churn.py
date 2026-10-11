"""
Module: test_churn.py
Description: Unit tests for baseline historical churn rate calculation using a 90-day threshold.
"""

import os
import pytest
import duckdb
from scripts.compute_churn import compute_baseline_churn

def test_compute_baseline_churn(tmp_path):
    """
    Test that customers are correctly flagged as churned based on a 90-day inactivity window.
    """
    
    parquet_file = tmp_path / "clean_transactions.parquet"
    db_file = str(tmp_path / "test_churn.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('1', 1, 10.0, 'Cust_A', '2010-12-20 10:00:00'::TIMESTAMP),
                ('2', 2, 20.0, 'Cust_B', '2010-09-01 15:00:00'::TIMESTAMP)
        ) AS t(Invoice, Quantity, Price, CustomerID, InvoiceDate);
    """)
    conn.execute(f"COPY mock_tx TO '{parquet_file}' (FORMAT PARQUET);")
    conn.close()
    
    churn_metrics = compute_baseline_churn(parquet_path=str(parquet_file), db_path=db_file, threshold_days=90)
    
    assert churn_metrics['total_customers'] == 2
    assert churn_metrics['churned_customers'] == 1
    assert churn_metrics['active_customers'] == 1
    assert churn_metrics['churn_rate_pct'] == 50.0