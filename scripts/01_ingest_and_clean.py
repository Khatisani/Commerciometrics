"""
Module: 01_ingest_and_clean.py
Description: Ingests raw multi-year retail transaction CSV data into a local DuckDB 
             staging database with robust handling for encoding and malformed rows.
"""

import os
import pandas as pd
import duckdb

DB_PATH = "data/processed/retail.duckdb"
CSV_PATH = "data/raw/online_retail_II.csv"

def run_ingestion():
    """
    Ingests the raw Online Retail II CSV dataset into a local DuckDB database.
    
    Parameters:
    -----------
    db_path : str
        Filepath to the target local DuckDB database.
    csv_path : str
        Filepath to the source raw CSV dataset.
        
    Returns:
    --------
    int
        Total number of valid rows successfully loaded into the 'raw_transactions' table.
        
    Raises:
    -------
    FileNotFoundError
        If the raw CSV file is missing from the specified path.
    """
    
    os.makedirs("data/processed", exist_ok=True)
    
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Raw dataset not found at {CSV_PATH}. Please ensure Task 1.1.3 is complete.")
    
    print(f"Reading CSV via pandas (using python engine and skipping bad lines) from {CSV_PATH}...")
    
    df = pd.read_csv(
        CSV_PATH, 
        encoding='latin-1', 
        dtype=str, 
        on_bad_lines='skip',
        encoding_errors='replace',
        engine='python'
    )
    
    print(f"Connecting to DuckDB at {DB_PATH}...")
    conn = duckdb.connect(DB_PATH)
    
    print("Writing cleaned DataFrame to DuckDB table 'raw_transactions'...")
    conn.execute("CREATE OR REPLACE TABLE raw_transactions AS SELECT * FROM df;")
    
    row_count = conn.execute("SELECT COUNT(*) FROM raw_transactions;").fetchone()[0]
    print(f"Ingestion complete! Loaded {row_count:,} valid rows into 'raw_transactions'.")
    
    conn.close()

if __name__ == "__main__":
    run_ingestion()