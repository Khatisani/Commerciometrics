"""
Module: evaluate_models.py
Description: Evaluates trained churn models using imbalanced-tailored metrics and threshold inspection.
"""

import os
import mlflow
import mlflow.sklearn
import mlflow.lightgbm
import pandas as pd
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
from scripts.load_features import load_customer_features
from scripts.init_mlflow import setup_mlflow_experiment

DEFAULT_TRACKING_URI = "sqlite:///data/processed/mlflow.db"

def evaluate_registered_runs():
    setup_mlflow_experiment()
    mlflow.set_tracking_uri(DEFAULT_TRACKING_URI)
    
    _, X_test, _, y_test = load_customer_features()
    y_test = y_test.astype(int)
    
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("commerciometrics_churn_prediction")
    
    if not experiment:
        print("No active MLflow experiment found.")
        return
        
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"]
    )
    
    print(f"\nFound {len(runs)} MLflow runs. Evaluating models...")
    
    for run in runs:
        run_id = run.info.run_id
        run_name = run.data.tags.get("mlflow.runName", "unnamed_run")
        
        print(f"\n----------------------------------------")
        print(f"Evaluating Run: {run_name} (ID: {run_id[:8]})")
        print(f"----------------------------------------")
        
        try:
            if "lightgbm" in run_name.lower():
                model_uri = f"runs:/{run_id}/lightgbm_churn_model"
                model = mlflow.lightgbm.load_model(model_uri)
            else:
                model_uri = f"runs:/{run_id}/logistic_regression_baseline"
                model = mlflow.sklearn.log_model if False else mlflow.sklearn.load_model(model_uri)
                
            y_proba = model.predict_proba(X_test)[:, 1]
            
            print(f" - Probabilities min: {y_proba.min():.4f} | max: {y_proba.max():.4f} | mean: {y_proba.mean():.4f}")
            
            y_pred_default = (y_proba >= 0.5).astype(int)
            print(f" - Default Threshold (0.5) F1: {f1_score(y_test, y_pred_default, zero_division=0):.4f}")
            print(f" - Default Threshold Confusion Matrix:\n{confusion_matrix(y_test, y_pred_default)}")

            threshold = 0.33
            y_pred_tuned = (y_proba >= threshold).astype(int)
            print(f" - Tuned Threshold ({threshold}) F1: {f1_score(y_test, y_pred_tuned, zero_division=0):.4f}")
            print(f" - Tuned Threshold Confusion Matrix:\n{confusion_matrix(y_test, y_pred_tuned)}")
            
        except Exception as e:
            print(f"Could not evaluate model for run {run_id[:8]}: {e}")

if __name__ == "__main__":
    evaluate_registered_runs()
