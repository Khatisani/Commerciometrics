"""
Module: compute_frequency.py
Description: Computes customer Frequency (total unique invoice count per customer).
"""

import os
import duckdb
import pandas as pd

DEFAULT_PARQUET_PATH = "data/processed/clean_transactions.parquet"
DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def compute_customer_frequency(parquet_path: str = DEFAULT_PARQUET_PATH, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Computes frequency (unique invoice count) for each customer from the parquet staging file.
    
    Parameters:
    -----------
    parquet_path : str
        Path to the cleaned transactions parquet file.
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing CustomerID and frequency.
    """

    
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Staging parquet file not found at {parquet_path}.")
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    print("Computing customer frequency metrics...")
    
    query = f"""
        SELECT 
            CustomerID,
            COUNT(DISTINCT Invoice) AS frequency
        FROM read_parquet('{parquet_path}')
        GROUP BY CustomerID
        ORDER BY frequency DESC;
    """
    
    df = conn.execute(query.strip()).fetchdf()
    
    conn.execute("CREATE OR REPLACE TABLE feature_frequency AS SELECT * FROM df;")
    conn.close()
    
    print(f"Frequency computed successfully for {len(df):,} customers.")
    return df

if __name__ == "__main__":
    compute_customer_frequency()