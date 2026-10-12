"""
Module: compute_diversity.py
Description: Computes product diversity (unique stock code count per customer).
"""

import os
import duckdb
import pandas as pd

DEFAULT_PARQUET_PATH = "data/processed/clean_transactions.parquet"
DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def compute_customer_diversity(parquet_path: str = DEFAULT_PARQUET_PATH, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Computes the number of unique stock codes purchased by each customer from the parquet staging file.
    
    Parameters:
    -----------
    parquet_path : str
        Path to the cleaned transactions parquet file.
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing CustomerID and unique_stock_codes.
    """


    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Staging parquet file not found at {parquet_path}.")
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    print("Computing customer product diversity metrics...")
    
    query = f"""
        SELECT 
            CustomerID,
            COUNT(DISTINCT StockCode) AS unique_stock_codes
        FROM read_parquet('{parquet_path}')
        GROUP BY CustomerID
        ORDER BY unique_stock_codes DESC;
    """
    
    df = conn.execute(query.strip()).fetchdf()
    
    conn.execute("CREATE OR REPLACE TABLE feature_diversity AS SELECT * FROM df;")
    conn.close()
    
    print(f"Product diversity computed successfully for {len(df):,} customers.")
    return df

if __name__ == "__main__":
    compute_customer_diversity()