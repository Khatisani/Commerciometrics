"""
Module: test_tenure.py
Description: Unit tests for customer Tenure calculation (days between first and last purchase).
"""

import duckdb
from scripts.compute_tenure import compute_customer_tenure

def test_compute_customer_tenure(tmp_path):
    """
    Test that customer tenure is correctly calculated as days between first and last purchase.
    """

    parquet_file = tmp_path / "clean_transactions.parquet"
    db_file = str(tmp_path / "test_tenure.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('INV-01', 1, 10.0, 'Cust_A', '2010-12-01 10:00:00'::TIMESTAMP),
                ('INV-02', 1, 20.0, 'Cust_A', '2010-12-11 11:00:00'::TIMESTAMP),
                ('INV-03', 1, 15.0, 'Cust_B', '2010-12-05 12:00:00'::TIMESTAMP)
        ) AS t(Invoice, Quantity, Price, CustomerID, InvoiceDate);
    """)
    conn.execute(f"COPY mock_tx TO '{parquet_file}' (FORMAT PARQUET);")
    conn.close()
    
    df_tenure = compute_customer_tenure(parquet_path=str(parquet_file), db_path=db_file)
    
    assert len(df_tenure) == 2
    
    cust_a = df_tenure[df_tenure['CustomerID'] == 'Cust_A'].iloc[0]
    cust_b = df_tenure[df_tenure['CustomerID'] == 'Cust_B'].iloc[0]
    
    assert int(cust_a['tenure_days']) == 10
    assert int(cust_b['tenure_days']) == 0