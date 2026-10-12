"""
Module: compute_tenure.py
Description: Computes customer Tenure (days between first and last purchase).
"""

import os
import duckdb
import pandas as pd

DEFAULT_PARQUET_PATH = "data/processed/clean_transactions.parquet"
DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def compute_customer_tenure(parquet_path: str = DEFAULT_PARQUET_PATH, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Computes tenure in days (first to last purchase) for each customer from the parquet staging file.
    
    Parameters:
    -----------
    parquet_path : str
        Path to the cleaned transactions parquet file.
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing CustomerID, first_purchase_date, last_purchase_date, and tenure_days.
    """


    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Staging parquet file not found at {parquet_path}.")
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    print("Computing customer tenure metrics...")
    
    query = f"""
        SELECT 
            CustomerID,
            MIN(InvoiceDate) AS first_purchase_date,
            MAX(InvoiceDate) AS last_purchase_date,
            DATE_DIFF('day', MIN(InvoiceDate), MAX(InvoiceDate)) AS tenure_days
        FROM read_parquet('{parquet_path}')
        GROUP BY CustomerID
        ORDER BY tenure_days DESC;
    """
    
    df = conn.execute(query.strip()).fetchdf()
    
    conn.execute("CREATE OR REPLACE TABLE feature_tenure AS SELECT * FROM df;")
    conn.close()
    
    print(f"Tenure computed successfully for {len(df):,} customers.")
    return df

if __name__ == "__main__":
    compute_customer_tenure()