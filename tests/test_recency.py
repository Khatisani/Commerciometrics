"""
Module: test_recency.py
Description: Unit tests for customer Recency calculation.
"""

import os
import pytest
import duckdb
from scripts.compute_recency import compute_customer_recency

def test_compute_customer_recency(tmp_path):
    """Test that customer recency is correctly calculated in days relative to dataset max date."""
    parquet_file = tmp_path / "clean_transactions.parquet"
    db_file = str(tmp_path / "test_recency.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('1', 1, 10.0, 'Cust_A', '2010-12-21 10:00:00'::TIMESTAMP),
                ('2', 2, 20.0, 'Cust_B', '2010-12-01 15:00:00'::TIMESTAMP),
                ('3', 1, 10.0, 'Cust_A', '2010-12-15 08:00:00'::TIMESTAMP)
        ) AS t(Invoice, Quantity, Price, CustomerID, InvoiceDate);
    """)
    conn.execute(f"COPY mock_tx TO '{parquet_file}' (FORMAT PARQUET);")
    conn.close()
    
    df_recency = compute_customer_recency(parquet_path=str(parquet_file), db_path=db_file)
    
    assert len(df_recency) == 2
    
    cust_a = df_recency[df_recency['CustomerID'] == 'Cust_A'].iloc[0]
    cust_b = df_recency[df_recency['CustomerID'] == 'Cust_B'].iloc[0]
    
    assert int(cust_a['recency_days']) == 10
    assert int(cust_b['recency_days']) == 30