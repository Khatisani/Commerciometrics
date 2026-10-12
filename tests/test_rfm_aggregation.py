"""
Module: test_rfm_aggregation.py
Description: Unit tests for aggregating Recency, Frequency, and Monetary features into a unified customer feature table.
"""

import duckdb
from scripts.aggregate_rfm import aggregate_customer_rfm

def test_aggregate_customer_rfm(tmp_path):
    """
    Test that individual RFM features are correctly joined into a single customer feature table.
    """
    
    db_file = str(tmp_path / "test_rfm.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute("""
        CREATE TABLE feature_recency AS SELECT * FROM (
            VALUES ('Cust_A', '2010-12-21', 10), ('Cust_B', '2010-12-01', 30)
        ) AS t(CustomerID, last_purchase_date, recency_days);
        
        CREATE TABLE feature_frequency AS SELECT * FROM (
            VALUES ('Cust_A', 2), ('Cust_B', 1)
        ) AS t(CustomerID, frequency);
        
        CREATE TABLE feature_monetary AS SELECT * FROM (
            VALUES ('Cust_A', 40.0), ('Cust_B', 25.0)
        ) AS t(CustomerID, monetary_value);
    """)
    conn.close()
    
    df_rfm = aggregate_customer_rfm(db_path=db_file)
    
    assert len(df_rfm) == 2
    assert list(df_rfm.columns) == ['CustomerID', 'last_purchase_date', 'recency_days', 'frequency', 'monetary_value']
    
    cust_a = df_rfm[df_rfm['CustomerID'] == 'Cust_A'].iloc[0]
    assert int(cust_a['recency_days']) == 10
    assert int(cust_a['frequency']) == 2
    assert float(cust_a['monetary_value']) == 40.0