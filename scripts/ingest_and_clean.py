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
DEFAULT_EXPORT_PATH = "data/processed/clean_transactions.parquet"

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


def run_remove_corrupted_pipeline(db_path: str = DEFAULT_DB_PATH, csv_path: str = DEFAULT_CSV_PATH) -> int:
    """
    Removes corrupted transaction rows (Quantity <= 0, Price <= 0, and non-product stock codes)
    and stores clean commercial sales records in the 'valid_transactions' table.
    
    Returns:
    --------
    int
        Total number of valid commercial transaction rows.
    """

    run_casting_pipeline(db_path=db_path, csv_path=csv_path)
    
    conn = duckdb.connect(db_path)
    
    print("Purging corrupted rows (Quantity <= 0, Price <= 0, and administrative stock codes)...")

    conn.execute("""
        CREATE OR REPLACE TABLE valid_transactions AS 
        SELECT * FROM typed_transactions 
        WHERE Quantity > 0 
          AND Price > 0
          AND StockCode NOT IN ('POST', 'DOT', 'M', 'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'PADS', 'POSTAGE', 'C2', 'D');
    """)
    
    valid_row_count = int(conn.execute("SELECT COUNT(*) FROM valid_transactions;").fetchone()[0])
    print(f"Purge complete! Retained {valid_row_count:,} valid commercial transaction rows in 'valid_transactions'.")
    
    conn.close()
    return valid_row_count

def run_export_pipeline(db_path: str = DEFAULT_DB_PATH, csv_path: str = DEFAULT_CSV_PATH, export_path: str = DEFAULT_EXPORT_PATH) -> int:
    """
    Exports the validated, typed, and purged transaction table to a compressed Parquet staging file.
    
    Returns:
    --------
    int
        Total number of rows exported to the Parquet staging layer.
    """

    run_remove_corrupted_pipeline(db_path=db_path, csv_path=csv_path)
    
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    
    conn = duckdb.connect(db_path)
    
    print(f"Exporting 'valid_transactions' to Parquet staging layer at {export_path}...")
    
    conn.execute(f"""
        COPY valid_transactions TO '{export_path}' (FORMAT PARQUET, COMPRESSION 'SNAPPY');
    """)
    
    export_row_count = int(conn.execute(f"SELECT COUNT(*) FROM read_parquet('{export_path}');").fetchone()[0])
    print(f"Export complete! Successfully wrote {export_row_count:,} rows to Parquet staging layer.")
    
    conn.close()
    return export_row_count

if __name__ == "__main__":
    run_export_pipeline()