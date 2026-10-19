"""
Module: test_data_loader.py
Description: Unit tests for the customer feature store data loading utility.
"""

import pandas as pd
import pytest
from scripts.load_features import load_customer_features

def test_load_customer_features_success(tmp_path):
    d = tmp_path / "processed"
    d.mkdir()
    file_path = d / "customer_features.parquet"
    
    mock_df = pd.DataFrame({
        "CustomerID": [101, 102, 103, 104],
        "Recency": [10, 20, 30, 40],
        "Frequency": [2, 4, 1, 5],
        "is_churned": [0, 1, 0, 1]
    })
    mock_df.to_parquet(file_path)
    
    X_train, X_test, y_train, y_test = load_customer_features(str(file_path), test_size=0.5, random_state=42)
    
    assert len(X_train) + len(X_test) == 4
    assert "CustomerID" not in X_train.columns
    assert "is_churned" not in X_train.columns
    assert len(y_train) == len(X_train)
    assert len(y_test) == len(X_test)

def test_load_customer_features_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_customer_features("non_existent_path.parquet")