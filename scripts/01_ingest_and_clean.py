import os
import duckdb


DB_PATH = "data/processed/retail.duckdb"
CSV_PATH = "data/raw/online_retail_II.csv"

def run_ingestion():
    os.makedirs("data/processed", exist_ok=True)
    
    print(f"Connecting to DuckDB at {DB_PATH}...")
    conn = duckdb.connect(DB_PATH)
    
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Raw dataset not found at {CSV_PATH}. Please ensure Task 1.1.3 is complete.")
    
    print(f"Ingesting raw CSV from {CSV_PATH} into table 'raw_transactions'...")
    
    conn.execute(f"""
        CREATE OR REPLACE TABLE raw_transactions AS 
        SELECT * FROM read_csv_auto('{CSV_PATH}', ALL_VARCHAR=1);
    """)


    row_count = conn.execute("SELECT COUNT(*) FROM raw_transactions;").fetchone()[0]
    print(f"Ingestion complete! Loaded {row_count:,} rows into 'raw_transactions'.")
    
    conn.close()

if __name__ == "__main__":
    run_ingestion()