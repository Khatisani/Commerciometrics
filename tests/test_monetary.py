"""
Module: test_monetary.py
Description: Unit tests for customer Monetary value calculation (total lifetime spend).
"""

import os
import pytest
import duckdb
from scripts.compute_monetary import compute_customer_monetary

def test_compute_customer_monetary(tmp_path):
    """
    Test that customer monetary value correctly sums total spend (Quantity * Price).
    """
    
    parquet_file = tmp_path / "clean_transactions.parquet"
    db_file = str(tmp_path / "test_monetary.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('INV-01', 2, 10.0, 'Cust_A', '2010-12-01 10:00:00'::TIMESTAMP),
                ('INV-02', 1, 20.0, 'Cust_A', '2010-12-05 11:00:00'::TIMESTAMP),
                ('INV-03', 5, 5.0, 'Cust_B', '2010-12-02 12:00:00'::TIMESTAMP)
        ) AS t(Invoice, Quantity, Price, CustomerID, InvoiceDate);
    """)
    conn.execute(f"COPY mock_tx TO '{parquet_file}' (FORMAT PARQUET);")
    conn.close()
    
    df_monetary = compute_customer_monetary(parquet_path=str(parquet_file), db_path=db_file)
    
    assert len(df_monetary) == 2
    
    cust_a = df_monetary[df_monetary['CustomerID'] == 'Cust_A'].iloc[0]
    cust_b = df_monetary[df_monetary['CustomerID'] == 'Cust_B'].iloc[0]
    
    assert float(cust_a['monetary_value']) == 40.0
    assert float(cust_b['monetary_value']) == 25.0