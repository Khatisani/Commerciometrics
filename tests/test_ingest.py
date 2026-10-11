import os
import pytest
import duckdb
from scripts.ingest_and_clean import run_ingestion

def test_ingestion_raises_error_on_missing_csv():
    """
    Test that ingestion raises FileNotFoundError when the source CSV is absent.
    """

    with pytest.raises(FileNotFoundError):
        run_ingestion(db_path="data/processed/test_retail.duckdb", csv_path="data/raw/non_existent.csv")

def test_ingestion_creates_duckdb_table(tmp_path):
    """
    Test that ingestion successfully creates the DuckDB table when provided a valid sample CSV.
    """

    csv_file = tmp_path / "sample_retail.csv"
    csv_file.write_text("Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer ID,Country\n489434,85048,15 PK ANSETT COLOUR TEA SPOONS,6,2009-12-01 07:45,2.55,13085,United Kingdom\n")
    
    db_file = str(tmp_path / "test_retail.duckdb")
    
    row_count = run_ingestion(db_path=db_file, csv_path=str(csv_file))
    
    assert row_count == 1
    
    conn = duckdb.connect(db_file)
    tables = [row[0] for row in conn.execute("SHOW TABLES;").fetchall()]
    conn.close()
    
    assert "raw_transactions" in tables