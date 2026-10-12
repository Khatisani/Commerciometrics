"""
Module: aggregate_behavioral.py
Description: Joins Tenure, Latency, and Diversity tables into a unified customer behavioral feature table in DuckDB.
"""

import os
import duckdb
import pandas as pd

DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def aggregate_customer_behavioral(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Joins feature_tenure, feature_latency, and feature_diversity tables into a single customer behavioral table.
    
    Parameters:
    -----------
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    pd.DataFrame
        Unified customer behavioral feature dataframe.
    """

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}.")
        
    conn = duckdb.connect(db_path)
    
    print("Aggregating advanced behavioral features into a unified customer feature table...")
    
    query = """
        SELECT 
            COALESCE(t.CustomerID, l.CustomerID, d.CustomerID) AS CustomerID,
            t.first_purchase_date,
            t.last_purchase_date,
            COALESCE(t.tenure_days, 0) AS tenure_days,
            COALESCE(l.avg_latency_days, 0.0) AS avg_latency_days,
            COALESCE(l.latency_variance, 0.0) AS latency_variance,
            COALESCE(d.unique_stock_codes, 0) AS unique_stock_codes
        FROM feature_tenure t
        FULL OUTER JOIN feature_latency l ON t.CustomerID = l.CustomerID
        FULL OUTER JOIN feature_diversity d ON COALESCE(t.CustomerID, l.CustomerID) = d.CustomerID
        ORDER BY tenure_days DESC;
    """
    
    df = conn.execute(query.strip()).fetchdf()
    
    conn.execute("CREATE OR REPLACE TABLE customer_behavioral AS SELECT * FROM df;")
    conn.close()
    
    print(f"Unified customer behavioral feature table created successfully with {len(df):,} customers.")
    return df

if __name__ == "__main__":
    aggregate_customer_behavioral()