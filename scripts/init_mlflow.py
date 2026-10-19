"""
Module: init_mlflow.py
Description: Initializes MLflow tracking environment, sets tracking URI, and configures the churn experiment.
"""

import os
import mlflow

DEFAULT_EXPERIMENT_NAME = "commerciometrics_churn_prediction"
DEFAULT_TRACKING_URI = "sqlite:///data/processed/mlflow.db"

def setup_mlflow_experiment(experiment_name: str = DEFAULT_EXPERIMENT_NAME, tracking_uri: str = DEFAULT_TRACKING_URI) -> str:
    """
    Initializes MLflow tracking URI and creates or activates the specified experiment.
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

if __name__ == "__main__":
    setup_mlflow_experiment()
