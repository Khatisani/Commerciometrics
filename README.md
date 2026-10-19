# Commerciometrics
Commercial analytics: an automated data pipeline that takes raw transaction data and transforms it into a clean, machine-learning-ready feature store.

Customers come and go, but every once in a while, regular buyers just quietly stop showing up. By the time you notice they're gone, it's already too late to win them back.

Retailers have mountains of raw transaction logs, but turning that messy data into actual insights—like figuring out who's about to churn—is a massive headache. Raw files come in weird formats, data gets corrupted, and building features like customer tenure or how long someone waits between purchases takes a ton of heavy lifting.

## Project Structure

```text
Commerciometrics/
├── data/
│   ├── raw/                      # Raw input datasets (e.g., Online Retail II)
│   └── processed/                # Intermediate tables & feature store outputs
│       ├── retail.duckdb         # Local analytical DuckDB database instance
│       ├── clean_transactions.parquet # Staging layer for cleaned commercial data
│       └── customer_features.parquet  # Official version-controlled feature store
├── outputs/                      # Generated analytical plots and figures
├── scripts/                      # Modular pipeline execution scripts
│   ├── ingest_and_clean.py       # Robust raw data ingestion and schema cleaning
│   ├── compute_recency.py        # Customer recency feature calculation
│   ├── compute_frequency.py      # Customer frequency feature calculation
│   ├── compute_monetary.py       # Customer monetary value calculation
│   ├── aggregate_rfm.py          # Unified RFM feature table aggregation
│   ├── compute_tenure.py         # Customer tenure feature calculation
│   ├── compute_latency.py        # Purchase latency and variance calculation
│   ├── compute_diversity.py      # Unique stock code / product diversity calculation
│   ├── aggregate_behavioral.py   # Unified behavioral feature table aggregation
│   ├── compute_churn.py          # Baseline 90-day churn target labeling
│   ├── build_feature_matrix.py   # Master feature matrix builder and joiner
│   ├── export_features.py        # Compressed Snappy Parquet feature store export
│   └── generate_plots.py         # Automated Pareto and visualization runner
├── tests/                        # Comprehensive unit and integration test suite
│   
├── run_pipeline.sh               # Automated pipeline shell orchestrator
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

## Quickstart 

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the pipeline 
```bash
cntrl +x run_pipeline.sh
./run_pipeline.sh
```



