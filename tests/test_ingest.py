import os
import pytest
import duckdb
from scripts.ingest_and_clean import run_ingestion
from scripts.ingest_and_clean import run_cleaning_pipeline
from scripts.ingest_and_clean import run_casting_pipeline
from scripts.ingest_and_clean import run_remove_corrupted_pipeline

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

def test_cleaning_filters_null_customer_ids(tmp_path):
    """
    Test that transactions with missing or null Customer IDs are filtered out.
    """
    
    csv_file = tmp_path / "sample_retail_nulls.csv"

    csv_file.write_text(
        "Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer ID,Country\n"
        "489434,85048,TEA SPOONS,6,2009-12-01 07:45,2.55,13085,United Kingdom\n"
        "489435,85049,COFFEE SPOONS,2,2009-12-01 07:50,1.50,,United Kingdom\n"
        "489436,85050,SUGAR SPOONS,1,2009-12-01 07:55,3.00,NULL,United Kingdom\n"
        "489437,85051,CREAM JUG,4,2009-12-01 08:00,4.25, ,United Kingdom\n"
    )
    
    db_file = str(tmp_path / "test_retail.duckdb")
    
    valid_rows = run_cleaning_pipeline(db_path=db_file, csv_path=str(csv_file))
    
    assert valid_rows == 1
    
    conn = duckdb.connect(db_file)
    customer_ids = conn.execute("SELECT \"Customer ID\" FROM clean_transactions;").fetchall()
    conn.close()
    
    assert len(customer_ids) == 1
    assert customer_ids[0][0] == '13085'

def test_casting_pipeline_types_and_revenue(tmp_path):
    """
    Test that data types are correctly cast to numeric and timestamp, enabling calculations.
    """
    
    csv_file = tmp_path / "sample_retail_types.csv"
    csv_file.write_text(
        "Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer ID,Country\n"
        "489434,85048,TEA SPOONS,5,2009-12-01 07:45:00,2.50,13085,United Kingdom\n"
        "489435,85049,COFFEE SPOONS,10,2009-12-01 08:15:00,1.20,13085,United Kingdom\n"
    )
    
    db_file = str(tmp_path / "test_retail.duckdb")

    row_count = run_casting_pipeline(db_path=db_file, csv_path=str(csv_file))
    assert row_count == 2
    
    conn = duckdb.connect(db_file)
    
    cols = {row[1]: row[2] for row in conn.execute("PRAGMA table_info('typed_transactions');").fetchall()}
    
    assert 'INTEGER' in cols['Quantity'].upper() or 'BIGINT' in cols['Quantity'].upper()
    assert 'DECIMAL' in cols['Price'].upper() or 'DOUBLE' in cols['Price'].upper() or 'FLOAT' in cols['Price'].upper()
    assert 'TIMESTAMP' in cols['InvoiceDate'].upper()
    
    total_revenue = conn.execute("SELECT SUM(Quantity * Price) FROM typed_transactions;").fetchone()[0]
    assert float(total_revenue) == 24.50
    
    conn.close()



def test_remove_corrupted_transactions(tmp_path):
    """
    Test that negative quantities, zero/negative prices, and non-product stock codes are removed.
    """
    
    csv_file = tmp_path / "sample_retail_corrupted.csv"
    csv_file.write_text(
        "Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer ID,Country\n"
        "489434,85048,TEA SPOONS,5,2009-12-01 07:45:00,2.50,13085,United Kingdom\n"      
        "489435,85049,COFFEE SPOONS,-2,2009-12-01 08:15:00,1.20,13085,United Kingdom\n"  
        "489436,POST,POSTAGE,1,2009-12-01 09:00:00,15.00,13085,United Kingdom\n"        
        "489437,85050,SUGAR SPOONS,3,2009-12-01 09:30:00,0.00,13085,United Kingdom\n"    
    )
    
    db_file = str(tmp_path / "test_retail.duckdb")
    
    row_count = run_remove_corrupted_pipeline(db_path=db_file, csv_path=str(csv_file))
    
    assert row_count == 1
    
    conn = duckdb.connect(db_file)
    stock_codes = [row[0] for row in conn.execute("SELECT StockCode FROM valid_transactions;").fetchall()]
    conn.close()
    
    assert stock_codes == ['85048']