"""
Module: finalize_model.py
Description: Extracts feature importances, serializes the final model artifact, and compiles an evaluation summary report.
"""

import os
import json
import joblib
import mlflow
import mlflow.lightgbm
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, confusion_matrix
from scripts.load_features import load_customer_features
from scripts.init_mlflow import setup_mlflow_experiment

def finalize_pipeline():
    os.makedirs("models", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    setup_mlflow_experiment()
    X_train, X_test, y_train, y_test = load_customer_features()
    y_test = y_test.astype(int)
    
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("commerciometrics_churn_prediction")
    
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="tags.mlflow.runName = 'lightgbm_churn_model'",
        order_by=["start_time DESC"],
        max_results=1
    )
    
    if not runs:
        print("No LightGBM run found. Ensure you have trained the LightGBM model first.")
        return
        
    latest_run = runs[0]
    run_id = latest_run.info.run_id
    print(f"Loading best LightGBM model from MLflow run: {run_id[:8]}...")
    
    model_uri = f"runs:/{run_id}/lightgbm_churn_model"
    model = mlflow.lightgbm.load_model(model_uri)
    
    model_path = "models/final_churn_model.pkl"
    joblib.dump(model, model_path)
    print(f"Serialized model artifact to {model_path}")
    
    feature_names = X_train.columns.tolist()
    importances = model.feature_importances_
    
    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values(by="importance", ascending=False)
    
    print("\nTop Features Driving Churn Prediction:")
    print(importance_df.to_string(index=False))
    
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.33).astype(int)
    
    metrics_summary = {
        "model_type": "LightGBM",
        "run_id": run_id,
        "test_samples": len(X_test),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "pr_auc": float(average_precision_score(y_test, y_proba)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "top_features": importance_df.head(5).to_dict(orient="records")
    }
    
    report_path = "reports/evaluation_summary.json"
    with open(report_path, "w") as f:
        json.dump(metrics_summary, f, indent=4)
        
    print(f"\nCompiled evaluation summary report saved to {report_path}")

if __name__ == "__main__":
    finalize_pipeline()
