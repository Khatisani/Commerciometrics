#!/bin/bash
set -e

echo "=== Step 0: Ingestion & Cleaning ==="
python3 scripts/ingest_and_clean.py

echo "=== Step 1: RFM Feature Generation ==="
python3 scripts/compute_recency.py
python3 scripts/compute_frequency.py
python3 scripts/compute_monetary.py
python3 scripts/aggregate_rfm.py

echo "=== Step 2: Advanced Behavioral Feature Generation ==="
python3 scripts/compute_tenure.py
python3 scripts/compute_latency.py
python3 scripts/compute_diversity.py
python3 scripts/aggregate_behavioral.py

echo "=== Step 3: Target Labeling & Feature Store Export ==="
python3 scripts/compute_target.py
python3 scripts/build_feature_matrix.py
python3 scripts/export_features.py

echo "=== Step 4: Running Test Suite ==="
pytest

echo "=== Pipeline Completed Successfully! ==="