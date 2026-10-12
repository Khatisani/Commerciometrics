"""
Module: test_behavioral_aggregation.py
Description: Unit tests for aggregating Tenure, Latency, and Diversity into a unified customer behavioral table.
"""

import duckdb
from scripts.aggregate_behavioral import aggregate_customer_behavioral

def test_aggregate_customer_behavioral(tmp_path):
    """
    Test that individual behavioral features are correctly joined into a single customer feature table.
    """


    db_file = str(tmp_path / "test_behavioral.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute("""
        CREATE TABLE feature_tenure AS SELECT * FROM (
            VALUES ('Cust_A', '2010-12-01', '2010-12-11', 10), ('Cust_B', '2010-12-05', '2010-12-05', 0)
        ) AS t(CustomerID, first_purchase_date, last_purchase_date, tenure_days);
        
        CREATE TABLE feature_latency AS SELECT * FROM (
            VALUES ('Cust_A', 5.0, 2.0), ('Cust_B', 0.0, 0.0)
        ) AS t(CustomerID, avg_latency_days, latency_variance);
        
        CREATE TABLE feature_diversity AS SELECT * FROM (
            VALUES ('Cust_A', 2), ('Cust_B', 3)
        ) AS t(CustomerID, unique_stock_codes);
    """)
    conn.close()
    
    df_beh = aggregate_customer_behavioral(db_path=db_file)
    
    assert len(df_beh) == 2
    assert 'tenure_days' in df_beh.columns
    assert 'avg_latency_days' in df_beh.columns
    assert 'latency_variance' in df_beh.columns
    assert 'unique_stock_codes' in df_beh.columns
    
    cust_a = df_beh[df_beh['CustomerID'] == 'Cust_A'].iloc[0]
    assert int(cust_a['tenure_days']) == 10
    assert float(cust_a['avg_latency_days']) == 5.0
    assert float(cust_a['latency_variance']) == 2.0
    assert int(cust_a['unique_stock_codes']) == 2