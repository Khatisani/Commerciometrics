"""
Module: test_latency.py
Description: Unit tests for purchase latency average and variance between consecutive orders.
"""

import os
import pytest
import duckdb
from scripts.compute_latency import compute_customer_latency

def test_compute_customer_latency(tmp_path):
    """
    Test that customer order latency average and variance are correctly computed.
    """
    
    parquet_file = tmp_path / "clean_transactions.parquet"
    db_file = str(tmp_path / "test_latency.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('INV-01', 1, 10.0, 'Cust_A', '2010-12-01 10:00:00'::TIMESTAMP),
                ('INV-02', 1, 20.0, 'Cust_A', '2010-12-05 11:00:00'::TIMESTAMP),
                ('INV-03', 1, 15.0, 'Cust_A', '2010-12-11 14:00:00'::TIMESTAMP),
                ('INV-04', 1, 50.0, 'Cust_B', '2010-12-02 12:00:00'::TIMESTAMP)
        ) AS t(Invoice, Quantity, Price, CustomerID, InvoiceDate);
    """)
    conn.execute(f"COPY mock_tx TO '{parquet_file}' (FORMAT PARQUET);")
    conn.close()
    
    df_latency = compute_customer_latency(parquet_path=str(parquet_file), db_path=db_file)
    
    assert len(df_latency) == 2
    
    cust_a = df_latency[df_latency['CustomerID'] == 'Cust_A'].iloc[0]
    cust_b = df_latency[df_latency['CustomerID'] == 'Cust_B'].iloc[0]
    
    assert float(cust_a['avg_latency_days']) == 5.0
    assert float(cust_a['latency_variance']) == 2.0
    assert float(cust_b['avg_latency_days']) == 0.0
    assert float(cust_b['latency_variance']) == 0.0