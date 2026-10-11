"""
Module: compute_pareto.py
Description: Computes cumulative customer revenue distribution and Pareto concentration 
             metrics to quantify revenue concentration (the 80/20 rule).
"""

import os
import duckdb
import pandas as pd

DEFAULT_PARQUET_PATH = "data/processed/clean_transactions.parquet"
DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def compute_customer_pareto(parquet_path: str = DEFAULT_PARQUET_PATH, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Computes customer-level total spend, ranks customers by revenue descending,
    and calculates cumulative revenue and customer percentage shares.
    
    Parameters:
    -----------
    parquet_path : str
        Path to the cleaned transactions parquet file.
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing customer rankings, total spend, and cumulative percentages.
    """
    
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Staging parquet file not found at {parquet_path}. Complete Iteration 1 first.")
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    print(f"Computing customer Pareto distribution from {parquet_path}...")
    

    query = f"""
        WITH customer_spend AS (
            SELECT 
                CustomerID,
                SUM(Quantity * Price) AS total_spend,
                COUNT(DISTINCT Invoice) AS total_orders,
                MAX(InvoiceDate) AS last_purchase_date
            FROM read_parquet('{parquet_path}')
            GROUP BY CustomerID
        ),
        ranked_customers AS (
            SELECT 
                CustomerID,
                total_spend,
                total_orders,
                last_purchase_date,
                ROW_NUMBER() OVER (ORDER BY total_spend DESC) as customer_rank,
                SUM(total_spend) OVER (ORDER BY total_spend DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_revenue,
                SUM(total_spend) OVER () as grand_total_revenue,
                COUNT(*) OVER () as total_customers
            FROM customer_spend
        )
        SELECT 
            CustomerID,
            total_spend,
            total_orders,
            last_purchase_date,
            customer_rank,
            ROUND((customer_rank * 100.0 / total_customers), 2) AS cum_customer_pct,
            ROUND((running_revenue * 100.0 / grand_total_revenue), 2) AS cum_revenue_pct
        FROM ranked_customers
        ORDER BY customer_rank ASC;
    """
    
    df_pareto = conn.execute(query).fetchdf()
    
    conn.execute("CREATE OR REPLACE TABLE customer_pareto AS SELECT * FROM df_pareto;")
    
    if not df_pareto.empty:
        total_custs = len(df_pareto)
        top_20_count = max(1, int(total_custs * 0.20))
        top_20_rev_share = df_pareto.iloc[top_20_count - 1]['cum_revenue_pct']
        print(f"Pareto Analysis Complete: Top 20% of customers ({top_20_count:,} accounts) drive {top_20_rev_share:.1f}% of total gross revenue.")
    
    conn.close()
    return df_pareto

if __name__ == "__main__":
    compute_customer_pareto()