"""
Module: load_features.py
Description: Utility for ingesting customer features from parquet and executing stratified splits.
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split

DEFAULT_FEATURE_STORE_PATH = "data/processed/customer_features.parquet"

def load_customer_features(feature_path: str = DEFAULT_FEATURE_STORE_PATH, test_size: float = 0.2, random_state: int = 42):
    """
    Ingests the customer feature store parquet file, drops identifiers and target, 
    and returns stratified train-test splits.
    """
    
    if not os.path.exists(feature_path):
        raise FileNotFoundError(f"Feature store not found at {feature_path}.")
        
    print(f"Loading feature store from {feature_path}...")
    df = pd.read_parquet(feature_path)
    
    target_col = "is_churned"
    drop_cols = ["CustomerID", target_col]
    
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' missing from feature store schema.")
        
    X = df.drop(columns=[col for col in drop_cols if col in df.columns])
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"Successfully loaded {len(df):,} records. Train split: {len(X_train):,} | Test split: {len(X_test):,}")
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    load_customer_features()
