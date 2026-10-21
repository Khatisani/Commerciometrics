#!/bin/bash
set -e

echo "=== Step 0: Ingestion & Cleaning ==="
python3 scripts/ingest_and_clean.py

echo "=== Step 1: RFM Feature Generation ==="
python3 scripts/compute_recency.py
python3 scripts/compute_frequency.py
python3 scripts/compute_monetary.py
python3 scripts/compute_pareto.py
python3 scripts/aggregate_rfm.py

echo "=== Step 2: Advanced Behavioral Feature Generation ==="
python3 scripts/compute_tenure.py
python3 scripts/compute_latency.py
python3 scripts/compute_diversity.py
python3 scripts/compute_timeline.py
python3 scripts/aggregate_behavioral.py

echo "=== Step 3: Target Labeling & Feature Store Export ==="
python3 scripts/compute_churn.py
python3 scripts/build_feature_matrix.py
python3 scripts/export_features.py

echo "=== Step 4: Model Training, Evaluation & Finalization ==="
python3 scripts/init_mlflow.py
python3 scripts/train_baseline.py
python3 scripts/train_lightgbm.py
python3 scripts/evaluate_models.py
python3 scripts/finalize_model.py
python3 scripts/generate_plots.py

echo "=== Step 5: Launching Streamlit Dashboard ==="
PYTHONPATH=. streamlit run app.py

echo "=== Pipeline Completed & Dashboard Running Successfully! ==="