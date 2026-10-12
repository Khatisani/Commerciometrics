"""
Module: test_timeline.py
Description: Unit tests for timeline boundary extraction (min and max transaction dates).
"""

import duckdb
from scripts.compute_timeline import get_dataset_timeline

def test_get_dataset_timeline(tmp_path):
    """
    Test that dataset min and max dates are correctly extracted to form the observation window.
    """
    
    parquet_file = tmp_path / "clean_transactions.parquet"
    db_file = str(tmp_path / "test_timeline.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('1', 1, 10.0, 'Cust_A', '2009-12-01 10:00:00'::TIMESTAMP),
                ('2', 2, 20.0, 'Cust_B', '2010-11-30 15:00:00'::TIMESTAMP)
        ) AS t(Invoice, Quantity, Price, CustomerID, InvoiceDate);
    """)
    conn.execute(f"COPY mock_tx TO '{parquet_file}' (FORMAT PARQUET);")
    conn.close()
    
    timeline = get_dataset_timeline(parquet_path=str(parquet_file), db_path=db_file)
    
    assert timeline['min_date'] == '2009-12-01 10:00:00'
    assert timeline['max_date'] == '2010-11-30 15:00:00'
    assert timeline['span_days'] >= 364