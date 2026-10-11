"""
Module: compute_timeline.py
Description: Computes and defines the observation window boundaries (Min and Max InvoiceDate)
             for RFM feature engineering and snapshot timing.
"""

import os
import duckdb

DEFAULT_PARQUET_PATH = "data/processed/clean_transactions.parquet"
DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def get_dataset_timeline(parquet_path: str = DEFAULT_PARQUET_PATH, db_path: str = DEFAULT_DB_PATH) -> dict:
    """
    Extracts the min and max transaction dates from the parquet staging file
    to establish the global observation window.
    
    Parameters:
    -----------
    parquet_path : str
        Path to the cleaned transactions parquet file.
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    dict
        Dictionary containing min_date, max_date, and span_days.
    """
    
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Staging parquet file not found at {parquet_path}. Complete Iteration 1 first.")
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    print(f"Extracting observation window boundaries from {parquet_path}...")
    
    query = f"""
        SELECT 
            MIN(InvoiceDate) AS min_date,
            MAX(InvoiceDate) AS max_date,
            DATE_DIFF('day', MIN(InvoiceDate), MAX(InvoiceDate)) AS span_days
        FROM read_parquet('{parquet_path}');
    """
    
    res = conn.execute(query.strip()).fetchone()
    
    timeline = {
        "min_date": str(res[0]),
        "max_date": str(res[1]),
        "span_days": int(res[2])
    }
    
    print(f"Observation Window Established: {timeline['min_date']} to {timeline['max_date']} ({timeline['span_days']:,} days span)")
    
    conn.close()
    return timeline

if __name__ == "__main__":
    get_dataset_timeline()