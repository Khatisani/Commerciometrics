"""
Module: export_features.py
Description: Exports the master customer feature matrix to a compressed feature store Parquet file.
"""

import os
import duckdb
import pandas as pd

DEFAULT_DB_PATH = "data/processed/retail.duckdb"
DEFAULT_OUTPUT_PATH = "data/processed/customer_features.parquet"

def export_customer_features(db_path: str = DEFAULT_DB_PATH, output_parquet_path: str = DEFAULT_OUTPUT_PATH) -> pd.DataFrame:
    """
    Exports the customer_feature_matrix table from DuckDB to a compressed Parquet file.
    
    Parameters:
    -----------
    db_path : str
        Path to the local DuckDB database.
    output_parquet_path : str
        Destination path for the feature store Parquet file.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame of the exported feature store.
    """

    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}.")
        
    os.makedirs(os.path.dirname(output_parquet_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    print(f"Exporting feature store table to {output_parquet_path}...")
    
    table_check = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'customer_feature_matrix'").fetchone()[0]
    if table_check == 0:
        raise ValueError("Table 'customer_feature_matrix' does not exist in DuckDB. Run feature matrix builder first.")
        

    query = f"""
        COPY customer_feature_matrix 
        TO '{output_parquet_path}' 
        (FORMAT PARQUET, COMPRESSION 'SNAPPY');
    """
    conn.execute(query)

    df = conn.execute("SELECT * FROM customer_feature_matrix;").fetchdf()
    conn.close()
    
    print(f"Feature store successfully exported with {len(df):,} rows and {len(df.columns)} columns.")
    return df

if __name__ == "__main__":
    export_customer_features()