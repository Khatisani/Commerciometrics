"""
Module: train_churn_model.py
Description: Phase 3.1 - MLflow Experiment Initialization, Feature Store Loading, and Stratified Splitting.
"""

import os
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split

DEFAULT_EXPERIMENT_NAME = "commerciometrics_churn_prediction"
DEFAULT_TRACKING_URI = "sqlite:///data/processed/mlflow.db"
FEATURE_STORE_PATH = "data/processed/customer_features.parquet"

def initialize_mlflow(experiment_name: str = DEFAULT_EXPERIMENT_NAME, tracking_uri: str = DEFAULT_TRACKING_URI) -> str:
    """
    Initializes MLflow tracking URI and experiment.
    """

    os.makedirs("data/processed", exist_ok=True)
    mlflow.set_tracking_uri(tracking_uri)
    
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
        print(f"Created new MLflow experiment '{experiment_name}' with ID: {experiment_id}")
    else:
        experiment_id = experiment.experiment_id
        print(f"Using existing MLflow experiment '{experiment_name}' (ID: {experiment_id})")
        
    mlflow.set_experiment(experiment_name)
    return experiment_id

def load_and_prepare_data(feature_path: str = FEATURE_STORE_PATH):
    """
    Loads the feature store and splits into features and stratified train-test sets.
    """
    
    if not os.path.exists(feature_path):
        raise FileNotFoundError(f"Feature store not found at {feature_path}. Run the pipeline first!")
        
    print(f"Loading feature store from {feature_path}...")
    df = pd.read_parquet(feature_path)
    print(f"Loaded {len(df):,} customer records with {len(df.columns)} columns.")
    
    target_col = "is_churned"
    drop_cols = ["CustomerID", target_col]
    
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' missing from feature store.")
        
    X = df.drop(columns=[col for col in drop_cols if col in df.columns])
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]:,} samples | Test set: {X_test.shape[0]:,} samples")
    print(f"Train churn rate: {y_train.mean():.2%} | Test churn rate: {y_test.mean():.2%}")
    
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    initialize_mlflow()
    X_train, X_test, y_train, y_test = load_and_prepare_data()