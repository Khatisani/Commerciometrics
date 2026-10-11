"""
Module: generate_plots.py
Description: Generates and saves commercial analytics visual artifacts (Pareto curve) 
             to the outputs directory.
"""

import os
import duckdb
import matplotlib.pyplot as plt

DEFAULT_DB_PATH = "data/processed/retail.duckdb"
DEFAULT_OUTPUT_DIR = "outputs"

def generate_pareto_plot(db_path: str = DEFAULT_DB_PATH, output_dir: str = DEFAULT_OUTPUT_DIR) -> str:
    """
    Queries customer Pareto metrics from DuckDB and saves a cumulative 
    revenue concentration chart to the outputs directory.
    
    Parameters:
    -----------
    db_path : str
        Path to the local DuckDB database.
    output_dir : str
        Directory path where output artifacts will be saved.
        
    Returns:
    --------
    str
        File path to the saved plot image.
    """
    
    os.makedirs(output_dir, exist_ok=True)
    conn = duckdb.connect(db_path)
    
    df = conn.execute("SELECT * FROM customer_pareto ORDER BY customer_rank ASC;").fetchdf()
    conn.close()
    
    if df.empty:
        raise ValueError("No customer Pareto data found in DuckDB. Run Pareto computation first.")
        
    plt.figure(figsize=(8, 6))
    plt.plot(df['cum_customer_pct'], df['cum_revenue_pct'], color='#ff69b4', lw=2.5, label='Cumulative Revenue')
    plt.plot([0, 100], [0, 100], color='gray', linestyle='--', label='Equality Line (1:1)')
    
    plt.title('Customer Revenue Concentration (Pareto Distribution)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Cumulative % of Customers', fontsize=10)
    plt.ylabel('Cumulative % of Revenue', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left')
    
    plot_path = os.path.join(output_dir, 'revenue_concentration.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Revenue concentration plot saved successfully to {plot_path}")
    return plot_path

if __name__ == "__main__":
    generate_pareto_plot()