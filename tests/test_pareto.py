"""
Module: test_pareto.py
Description: Unit tests for customer Pareto revenue concentration analysis.
"""

import os
import pytest
import duckdb
from scripts.compute_pareto import compute_customer_pareto

def test_compute_customer_pareto(tmp_path):
    """
    Test that customer Pareto metrics correctly calculate cumulative revenue concentration.
    """
    
    parquet_file = tmp_path / "clean_transactions.parquet"
    db_file = str(tmp_path / "test_pareto.duckdb")
    

    conn = duckdb.connect(db_file)
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('1', 'CUST_VIP', 10.0, 100.0), -- Customer A spends 1000
                ('2', 'CUST_MID', 5.0, 100.0),  -- Customer B spends 500
                ('3', 'CUST_LOW', 1.0, 100.0)   -- Customer C spends 100
        ) AS t(Invoice, StockCode, Quantity, Price);
    """)

    conn.execute("DROP TABLE mock_tx;")
    conn.execute(f"""
        CREATE TABLE mock_tx AS SELECT * FROM (
            VALUES 
                ('1', 10, 100.0, 'Cust_A'),
                ('2', 5, 100.0, 'Cust_B'),
                ('3', 1, 100.0, 'Cust_C')
        ) AS t(Invoice, Quantity, Price, CustomerID);
    """)
    conn.execute(f"COPY mock_tx TO '{parquet_file}' (FORMAT PARQUET);")
    conn.close()
    

    df_pareto = compute_customer_pareto(parquet_path=str(parquet_file), db_path=db_file)
    
    assert len(df_pareto) == 3

    assert df_pareto.iloc[0]['CustomerID'] == 'Cust_A'
    assert float(df_pareto.iloc[0]['total_spend']) == 1000.0

    assert float(df_pareto.iloc[-1]['cum_revenue_pct']) == 100.0