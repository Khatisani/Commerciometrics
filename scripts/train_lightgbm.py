"""
Module: train_lightgbm.py
Description: Trains an optimized LightGBM classifier for customer churn prediction with MLflow logging.
"""

import mlflow
import mlflow.lightgbm
import lightgbm as lgb
import numpy as np
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

def train_lightgbm_model():
    setup_mlflow_experiment()
    
    X_train, X_test, y_train, y_test = load_customer_features()
    
    y_train = y_train.astype(int)
    y_test = y_test.astype(int)
    

    neg_count = np.sum(y_train == 0)
    pos_count = np.sum(y_train == 1)
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
    
    params = {
        "objective": "binary",
        "metric": "auc",
        "boosting_type": "gbdt",
        "learning_rate": 0.05,
        "max_depth": 6,
        "n_estimators": 150,
        "scale_pos_weight": scale_pos_weight,
        "random_state": 42,
        "verbose": -1
    }
    
    print("\nTraining LightGBM classifier...")
    with mlflow.start_run(run_name="lightgbm_churn_model"):
        mlflow.log_params(params)
        

        model = lgb.LGBMClassifier(**params)
        model.fit(
            X_train, y_train,
            eval_X=X_test,
            eval_y=y_test,
            callbacks=[lgb.early_stopping(stopping_rounds=20, verbose=False)]
        )
        
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
        mlflow.lightgbm.log_model(model, name="lightgbm_churn_model")
        
        print("\nLightGBM Evaluation Metrics:")
        for metric, value in metrics.items():
            print(f" - {metric}: {value:.4f}")
            
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, zero_division=0))

if __name__ == "__main__":
    train_lightgbm_model()
