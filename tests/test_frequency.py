"""
Module: test_frequency.py
Description: Unit tests for customer Frequency calculation (unique invoice count).
"""

import os
import pytest
import duckdb
from scripts.compute_frequency import compute_customer_frequency

def test_compute_customer_frequency(tmp_path):
    """
    Test that customer frequency correctly counts unique invoices per customer.
    """

    parquet_file = tmp_path / "clean_transactions.parquet"
    db_file = str(tmp_path / "test_frequency.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('INV-01', 1, 10.0, 'Cust_A', '2010-12-01 10:00:00'::TIMESTAMP),
                ('INV-01', 2, 15.0, 'Cust_A', '2010-12-01 10:00:00'::TIMESTAMP),
                ('INV-02', 1, 20.0, 'Cust_A', '2010-12-05 11:00:00'::TIMESTAMP),
                ('INV-03', 1, 50.0, 'Cust_B', '2010-12-02 12:00:00'::TIMESTAMP)
        ) AS t(Invoice, Quantity, Price, CustomerID, InvoiceDate);
    """)
    
    conn.execute(f"COPY mock_tx TO '{parquet_file}' (FORMAT PARQUET);")
    conn.close()
    
    df_freq = compute_customer_frequency(parquet_path=str(parquet_file), db_path=db_file)
    
    assert len(df_freq) == 2
    
    cust_a = df_freq[df_freq['CustomerID'] == 'Cust_A'].iloc[0]
    cust_b = df_freq[df_freq['CustomerID'] == 'Cust_B'].iloc[0]
    
    assert int(cust_a['frequency']) == 2
    assert int(cust_b['frequency']) == 1