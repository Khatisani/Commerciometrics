"""
Module: train_baseline.py
Description: Trains a baseline Logistic Regression model with class balancing and logs metrics to MLflow.
"""

import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)
from scripts.load_features import load_customer_features
from scripts.init_mlflow import setup_mlflow_experiment

def train_baseline():
    setup_mlflow_experiment()

    X_train, X_test, y_train, y_test = load_customer_features()
    
    params = {
        "model_type": "LogisticRegression",
        "class_weight": "balanced",
        "random_state": 42,
        "max_iter": 1000
    }
    
    print("\nTraining baseline Logistic Regression model...")
    with mlflow.start_run(run_name="baseline_logistic_regression"):
        mlflow.log_params(params)
        
        model = LogisticRegression(
            class_weight=params["class_weight"],
            random_state=params["random_state"],
            max_iter=params["max_iter"]
        )
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        metrics = {
            "roc_auc": roc_auc_score(y_test, y_proba),
            "pr_auc": average_precision_score(y_test, y_proba),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1_score": f1_score(y_test, y_pred, zero_division=0)
        }
        
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "logistic_regression_baseline")
        
        print("\nBaseline Evaluation Metrics:")
        for metric, value in metrics.items():
            print(f" - {metric}: {value:.4f}")
            
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, zero_division=0))

if __name__ == "__main__":
    train_baseline()
