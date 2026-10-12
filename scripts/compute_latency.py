"""
Module: compute_latency.py
Description: Computes purchase latency average and variance between consecutive orders per customer.
"""

import os
import duckdb
import pandas as pd

DEFAULT_PARQUET_PATH = "data/processed/clean_transactions.parquet"
DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def compute_customer_latency(parquet_path: str = DEFAULT_PARQUET_PATH, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Computes average and variance of days between consecutive orders for each customer.
    
    Parameters:
    -----------
    parquet_path : str
        Path to the cleaned transactions parquet file.
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing CustomerID, avg_latency_days, and latency_variance.
    """
    
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Staging parquet file not found at {parquet_path}.")
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    print("Computing customer purchase latency metrics...")
    
    query = f"""
        WITH customer_invoices AS (
            SELECT DISTINCT 
                CustomerID, 
                CAST(InvoiceDate AS DATE) AS order_date
            FROM read_parquet('{parquet_path}')
        ),
        ordered_invoices AS (
            SELECT 
                CustomerID,
                order_date,
                LAG(order_date) OVER (PARTITION BY CustomerID ORDER BY order_date) AS prev_order_date
            FROM customer_invoices
        ),
        latency_calc AS (
            SELECT 
                CustomerID,
                DATE_DIFF('day', prev_order_date, order_date) AS days_between_orders
            FROM ordered_invoices
            WHERE prev_order_date IS NOT NULL
        ),
        all_customers AS (
            SELECT DISTINCT CustomerID FROM read_parquet('{parquet_path}')
        ),
        customer_latency_agg AS (
            SELECT 
                CustomerID,
                AVG(days_between_orders) AS avg_latency_days,
                COALESCE(VAR_SAMP(days_between_orders), 0.0) AS latency_variance
            FROM latency_calc
            GROUP BY CustomerID
        )
        SELECT 
            ac.CustomerID,
            COALESCE(cla.avg_latency_days, 0.0) AS avg_latency_days,
            COALESCE(cla.latency_variance, 0.0) AS latency_variance
        FROM all_customers ac
        LEFT JOIN customer_latency_agg cla ON ac.CustomerID = cla.CustomerID
        ORDER BY avg_latency_days DESC;
    """
    
    df = conn.execute(query.strip()).fetchdf()
    
    conn.execute("CREATE OR REPLACE TABLE feature_latency AS SELECT * FROM df;")
    conn.close()
    
    print(f"Latency computed successfully for {len(df):,} customers.")
    return df

if __name__ == "__main__":
    compute_customer_latency()