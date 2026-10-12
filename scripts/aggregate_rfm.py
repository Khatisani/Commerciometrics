"""
Module: aggregate_rfm.py
Description: Joins Recency, Frequency, and Monetary tables into a unified customer RFM feature table in DuckDB.
"""

import os
import duckdb
import pandas as pd

DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def aggregate_customer_rfm(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Joins feature_recency, feature_frequency, and feature_monetary tables into a single customer RFM table.
    
    Parameters:
    -----------
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    pd.DataFrame
        Unified customer RFM feature dataframe.
    """
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}.")
        
    conn = duckdb.connect(db_path)
    
    print("Aggregating RFM features into a unified customer feature table...")
    
    query = """
        SELECT 
            COALESCE(r.CustomerID, f.CustomerID, m.CustomerID) AS CustomerID,
            r.last_purchase_date,
            r.recency_days,
            f.frequency,
            m.monetary_value
        FROM feature_recency r
        FULL OUTER JOIN feature_frequency f ON r.CustomerID = f.CustomerID
        FULL OUTER JOIN feature_monetary m ON COALESCE(r.CustomerID, f.CustomerID) = m.CustomerID
        ORDER BY m.monetary_value DESC;
    """
    
    df = conn.execute(query.strip()).fetchdf()


    conn.execute("CREATE OR REPLACE TABLE customer_rfm AS SELECT * FROM df;")
    conn.close()
    
    print(f"Unified customer RFM feature table created successfully with {len(df):,} customers.")
    return df

if __name__ == "__main__":
    aggregate_customer_rfm()