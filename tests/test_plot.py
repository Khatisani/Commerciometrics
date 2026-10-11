"""
Module: test_plots.py
Description: Unit tests for visual artifact generation (revenue concentration plots).
"""

import os
import duckdb
from scripts.generate_plots import generate_pareto_plot

def test_generate_pareto_plot(tmp_path):
    """
    Test that the Pareto revenue concentration plot is successfully generated and saved.
    """
    
    output_dir = tmp_path / "outputs"
    db_file = str(tmp_path / "test_plots.duckdb")
    
    conn = duckdb.connect(db_file)
    conn.execute("""
        CREATE TABLE customer_pareto AS SELECT * FROM (
            VALUES 
                ('Cust_A', 1000.0, 10, '2010-12-01', 1, 33.33, 50.0),
                ('Cust_B', 800.0, 5, '2010-11-01', 2, 66.67, 90.0),
                ('Cust_C', 200.0, 1, '2010-10-01', 3, 100.0, 100.0)
        ) AS t(CustomerID, total_spend, total_orders, last_purchase_date, customer_rank, cum_customer_pct, cum_revenue_pct);
    """)
    conn.close()
    
    plot_path = generate_pareto_plot(db_path=db_file, output_dir=str(output_dir))
    assert os.path.exists(plot_path)
    assert os.path.getsize(plot_path) > 0