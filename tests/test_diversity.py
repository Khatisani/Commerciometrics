"""
Module: test_diversity.py
Description: Unit tests for customer product diversity (unique stock code count).
"""

import duckdb
from scripts.compute_diversity import compute_customer_diversity

def test_compute_customer_diversity(tmp_path):
    """
    Test that customer product diversity correctly counts unique stock codes.
    """

    parquet_file = tmp_path / "clean_transactions.parquet"
    db_file = str(tmp_path / "test_diversity.duckdb")

    conn = duckdb.connect(db_file)
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('INV-01', 'A1', 2, 10.0, 'Cust_A', '2010-12-01 10:00:00'::TIMESTAMP),
                ('INV-02', 'A1', 1, 10.0, 'Cust_A', '2010-12-05 11:00:00'::TIMESTAMP),
                ('INV-03', 'B2', 1, 20.0, 'Cust_A', '2010-12-08 14:00:00'::TIMESTAMP),
                ('INV-04', 'C3', 5, 5.0, 'Cust_B', '2010-12-02 12:00:00'::TIMESTAMP),
                ('INV-05', 'D4', 2, 15.0, 'Cust_B', '2010-12-03 13:00:00'::TIMESTAMP),
                ('INV-06', 'E5', 1, 25.0, 'Cust_B', '2010-12-04 15:00:00'::TIMESTAMP)
        ) AS t(Invoice, StockCode, Quantity, Price, CustomerID, InvoiceDate);
    """)

    conn.execute(f"COPY mock_tx TO '{parquet_file}' (FORMAT PARQUET);")
    conn.close()
    
    df_diversity = compute_customer_diversity(parquet_path=str(parquet_file), db_path=db_file)
    
    assert len(df_diversity) == 2
    
    cust_a = df_diversity[df_diversity['CustomerID'] == 'Cust_A'].iloc[0]
    cust_b = df_diversity[df_diversity['CustomerID'] == 'Cust_B'].iloc[0]
    
    assert int(cust_a['unique_stock_codes']) == 2
    assert int(cust_b['unique_stock_codes']) == 3