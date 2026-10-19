"""
Module: build_feature_matrix.py
Description: Joins RFM features, behavioral features, and churn target labels into a master feature matrix.
"""

import os
import duckdb
import pandas as pd

DEFAULT_DB_PATH = "data/processed/retail.duckdb"

def build_customer_feature_matrix(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Programmatically joins customer_rfm, customer_behavioral, and feature_target tables 
    into a unified master customer feature matrix.
    
    Parameters:
    -----------
    db_path : str
        Path to the local DuckDB database.
        
    Returns:
    --------
    pd.DataFrame
        Master customer feature matrix dataframe.
    """

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}.")
        
    conn = duckdb.connect(db_path)
    
    print("Building master customer feature matrix with churn target labels...")

    tables = [row[0] for row in conn.execute("SHOW TABLES;").fetchall()]
    churn_table = "customer_churn_status" if "customer_churn_status" in tables else "feature_target"
    print(f"Using churn target table: '{churn_table}'")

    query = f"""
        SELECT 
            rfm.CustomerID,
            rfm.recency_days,
            rfm.frequency,
            rfm.monetary_value,
            beh.tenure_days,
            beh.avg_latency_days,
            beh.latency_variance,
            beh.unique_stock_codes,
            tgt.is_churned
        FROM customer_rfm rfm
        LEFT JOIN customer_behavioral beh ON rfm.CustomerID = beh.CustomerID
        LEFT JOIN {churn_table} tgt ON rfm.CustomerID = tgt.CustomerID
        ORDER BY rfm.monetary_value DESC;
    """

    df = conn.execute(query.strip()).fetchdf()
    
    conn.execute("CREATE OR REPLACE TABLE customer_feature_matrix AS SELECT * FROM df;")
    
    os.makedirs("data/processed", exist_ok=True)
    conn.execute("COPY customer_feature_matrix TO 'data/processed/customer_feature_matrix.parquet' (FORMAT PARQUET);")
    
    conn.close()
    
    churn_count = df['is_churned'].sum() if 'is_churned' in df.columns else 0
    print(f"Master feature matrix built successfully with {len(df):,} customers and {len(df.columns)} features ({churn_count:,} churned).")
    return df

if __name__ == "__main__":
    build_customer_feature_matrix()