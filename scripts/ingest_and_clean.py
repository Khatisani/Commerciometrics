"""
Module: ingest_and_clean.py
Description: Ingests raw multi-year retail transaction CSV data into a local DuckDB 
             staging database with robust handling for encoding and malformed rows.
"""

import os
import pandas as pd
import duckdb

DEFAULT_DB_PATH = "data/processed/retail.duckdb"
DEFAULT_CSV_PATH = "data/raw/online_retail_II.csv"

def run_ingestion(db_path: str = DEFAULT_DB_PATH, csv_path: str = DEFAULT_CSV_PATH) -> int:
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

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Raw dataset not found at {csv_path}. Please verify data placement.")
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"Reading CSV via pandas (using python engine and skipping bad lines) from {csv_path}...")
    
    df = pd.read_csv(
        csv_path, 
        encoding='latin-1', 
        dtype=str, 
        on_bad_lines='skip',
        encoding_errors='replace',
        engine='python'
    )
    
    print(f"Connecting to DuckDB at {db_path}...")
    conn = duckdb.connect(db_path)
    
    print("Writing cleaned DataFrame to DuckDB table 'raw_transactions'...")
    conn.execute("CREATE OR REPLACE TABLE raw_transactions AS SELECT * FROM df;")
    
    row_count = int(conn.execute("SELECT COUNT(*) FROM raw_transactions;").fetchone()[0])
    print(f"Ingestion complete! Loaded {row_count:,} valid rows into 'raw_transactions'.")
    
    conn.close()
    return row_count

def run_cleaning_pipeline(db_path: str = DEFAULT_DB_PATH, csv_path: str = DEFAULT_CSV_PATH) -> int:
    """
    Ingests raw data and filters out rows with missing, null, or empty Customer IDs,
    storing the result in a new 'clean_transactions' table.
    
    Returns:
    --------
    int
        Total number of valid rows after cleaning.
    """

    run_ingestion(db_path=db_path, csv_path=csv_path)
    
    conn = duckdb.connect(db_path)
    
    print("Filtering out rows with missing or null Customer IDs...")

    conn.execute("""
        CREATE OR REPLACE TABLE clean_transactions AS 
        SELECT * FROM raw_transactions 
        WHERE "Customer ID" IS NOT NULL 
          AND TRIM(CAST("Customer ID" AS VARCHAR)) != ''
          AND UPPER(TRIM(CAST("Customer ID" AS VARCHAR))) != 'NULL'
          AND UPPER(TRIM(CAST("Customer ID" AS VARCHAR))) != 'NAN';
    """)
    
    clean_row_count = int(conn.execute("SELECT COUNT(*) FROM clean_transactions;").fetchone()[0])
    print(f"Cleaning complete! Retained {clean_row_count:,} valid customer transaction rows.")
    
    conn.close()
    return clean_row_count

def run_casting_pipeline(db_path: str = DEFAULT_DB_PATH, csv_path: str = DEFAULT_CSV_PATH) -> int:
    """
    Casts cleaned transaction columns into appropriate numeric and temporal data types,
    persisting the result in the 'typed_transactions' table.
    
    Returns:
    --------
    int
        Total number of rows in the typed table.
    """
    
    run_cleaning_pipeline(db_path=db_path, csv_path=csv_path)
    
    conn = duckdb.connect(db_path)
    
    print("Casting columns to appropriate data types (Quantity -> INTEGER, Price -> DECIMAL, InvoiceDate -> TIMESTAMP)...")
    conn.execute("""
        CREATE OR REPLACE TABLE typed_transactions AS 
        SELECT 
            CAST(Invoice AS VARCHAR) AS Invoice,
            CAST(StockCode AS VARCHAR) AS StockCode,
            CAST(Description AS VARCHAR) AS Description,
            CAST(Quantity AS INTEGER) AS Quantity,
            CAST(InvoiceDate AS TIMESTAMP) AS InvoiceDate,
            CAST(Price AS DECIMAL(10,2)) AS Price,
            CAST("Customer ID" AS VARCHAR) AS CustomerID,
            CAST(Country AS VARCHAR) AS Country
        FROM clean_transactions;
    """)
    
    typed_row_count = int(conn.execute("SELECT COUNT(*) FROM typed_transactions;").fetchone()[0])
    print(f"Casting complete! Staged {typed_row_count:,} strongly-typed rows into 'typed_transactions'.")
    
    conn.close()
    return typed_row_count

if __name__ == "__main__":
    run_casting_pipeline()