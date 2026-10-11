"""
Module: compute_churn.py
Description: Computes baseline historical churn rate using a configurable inactivity threshold 
             relative to the global maximum transaction date.
"""

import os
import duckdb

DEFAULT_PARQUET_PATH = "data/processed/clean_transactions.parquet"
DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def compute_baseline_churn(parquet_path: str = DEFAULT_PARQUET_PATH, db_path: str = DEFAULT_DB_PATH, threshold_days: int = 90) -> dict:
    """
    Computes customer-level recency relative to the dataset's max date and calculates 
    the proportion of customers exceeding the inactivity threshold (churn rate).
    
    Parameters:
    -----------
    parquet_path : str
        Path to the cleaned transactions parquet file.
    db_path : str
        Path to the local DuckDB database.
    threshold_days : int
        Number of days of inactivity required to classify a customer as churned (default: 90).
        
    Returns:
    --------
    dict
        Dictionary containing total customers, churned count, active count, and churn rate percentage.
    """

    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Staging parquet file not found at {parquet_path}. Complete Iteration 1 first.")
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    print(f"Computing baseline churn rate ({threshold_days}-day threshold) from {parquet_path}...")
    
    query = f"""
        WITH global_bounds AS (
            SELECT MAX(InvoiceDate) AS max_dataset_date FROM read_parquet('{parquet_path}')
        ),
        customer_recency AS (
            SELECT 
                CustomerID,
                MAX(InvoiceDate) AS last_purchase_date,
                DATE_DIFF('day', MAX(InvoiceDate), (SELECT max_dataset_date FROM global_bounds)) AS days_inactive
            FROM read_parquet('{parquet_path}')
            GROUP BY CustomerID
        ),
        churn_flags AS (
            SELECT 
                CustomerID,
                last_purchase_date,
                days_inactive,
                CASE WHEN days_inactive > {threshold_days} THEN 1 ELSE 0 END AS is_churned
            FROM customer_recency
        )
        SELECT 
            COUNT(*) AS total_customers,
            SUM(is_churned) AS churned_customers,
            COUNT(*) - SUM(is_churned) AS active_customers,
            ROUND(SUM(is_churned) * 100.0 / COUNT(*), 2) AS churn_rate_pct
        FROM churn_flags;
    """
    
    res = conn.execute(query.strip()).fetchone()
    
    metrics = {
        "total_customers": int(res[0]),
        "churned_customers": int(res[1]),
        "active_customers": int(res[2]),
        "churn_rate_pct": float(res[3])
    }
    
    conn.execute(f"""
        CREATE OR REPLACE TABLE customer_churn_status AS 
        WITH global_bounds AS (
            SELECT MAX(InvoiceDate) AS max_dataset_date FROM read_parquet('{parquet_path}')
        )
        SELECT 
            CustomerID,
            MAX(InvoiceDate) AS last_purchase_date,
            DATE_DIFF('day', MAX(InvoiceDate), (SELECT max_dataset_date FROM global_bounds)) AS days_inactive,
            CASE WHEN DATE_DIFF('day', MAX(InvoiceDate), (SELECT max_dataset_date FROM global_bounds)) > {threshold_days} 
            THEN 1 ELSE 0 END AS is_churned
        FROM read_parquet('{parquet_path}')
        GROUP BY CustomerID;
    """)
    
    print(f"Baseline Churn Analysis Complete: {metrics['churned_customers']:,} / {metrics['total_customers']:,} customers churned ({metrics['churn_rate_pct']}% hurn rate using a {threshold_days}-day window).")
    
    conn.close()
    return metrics

if __name__ == "__main__":
    compute_baseline_churn()