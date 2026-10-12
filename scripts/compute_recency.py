"""
Module: compute_recency.py
Description: Computes customer Recency (days since last purchase relative to max dataset date).
"""

import os
import duckdb
import pandas as pd

DEFAULT_PARQUET_PATH = "data/processed/clean_transactions.parquet"
DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def compute_customer_recency(parquet_path: str = DEFAULT_PARQUET_PATH, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Computes recency in days for each customer relative to the global max transaction date.
    
    Parameters:
    -----------
    parquet_path : str
        Path to the cleaned transactions parquet file.
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing CustomerID, last_purchase_date, and recency_days.
    """
    
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Staging parquet file not found at {parquet_path}.")
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    print("Computing customer recency metrics...")
    
    query = f"""
        WITH global_bounds AS (
            SELECT MAX(InvoiceDate) AS max_dataset_date FROM read_parquet('{parquet_path}')
        ),
        customer_last_purchase AS (
            SELECT 
                CustomerID,
                MAX(InvoiceDate) AS last_purchase_date
            FROM read_parquet('{parquet_path}')
            GROUP BY CustomerID
        )
        SELECT 
            clp.CustomerID,
            clp.last_purchase_date,
            DATE_DIFF('day', clp.last_purchase_date, gb.max_dataset_date) AS recency_days
        FROM customer_last_purchase clp
        CROSS JOIN global_bounds gb
        ORDER BY recency_days ASC;
    """
    
    df = conn.execute(query.strip()).fetchdf()
    
    conn.execute("CREATE OR REPLACE TABLE feature_recency AS SELECT * FROM df;")
    conn.close()
    
    print(f"Recency computed successfully for {len(df):,} customers.")
    return df

if __name__ == "__main__":
    compute_customer_recency()