import os
import requests
import pandas as pd

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

# Make sure directories exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# URL of the dataset on UCI Machine Learning Repository
DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx"
EXCEL_PATH = os.path.join(RAW_DIR, "online_retail_II.xlsx")

def download_dataset():
    """Downloads the Excel file from UCI repository if not already present."""
    if os.path.exists(EXCEL_PATH):
        print(f"Dataset already exists at: {EXCEL_PATH}. Skipping download.")
        return
    
    print(f"Downloading dataset from: {DATA_URL}")
    print("This file is ~45MB and may take a minute or two depending on connection speed...")
    response = requests.get(DATA_URL, stream=True)
    response.raise_for_status()
    
    with open(EXCEL_PATH, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("Download complete.")

def split_and_simulate_sources():
    """Reads the Excel sheets, merges them, and splits into 6 regional legacy files."""
    print("Reading Excel sheets... (this requires 'openpyxl' and may take a moment)")
    
    # Read both sheets from the Excel file
    try:
        df_09_10 = pd.read_excel(EXCEL_PATH, sheet_name="Year 2009-2010")
        print(f"Loaded Sheet 1 (2009-2010): {len(df_09_10)} rows")
        
        df_10_11 = pd.read_excel(EXCEL_PATH, sheet_name="Year 2010-2011")
        print(f"Loaded Sheet 2 (2010-2011): {len(df_10_11)} rows")
    except Exception as e:
        print(f"Error reading Excel sheets: {e}")
        print("Please check that the file is not corrupted and 'openpyxl' is installed.")
        return

    # Combine datasets
    df_combined = pd.concat([df_09_10, df_10_11], ignore_index=True)
    print(f"Combined dataset: {len(df_combined)} total rows")

    # Map countries to regional groups to simulate separate systems
    # 1. UK (United Kingdom) - by far the largest, we split it by year to make 2 files
    df_uk = df_combined[df_combined['Country'] == 'United Kingdom']
    df_uk_2010 = df_uk[df_uk['InvoiceDate'] < '2011-01-01']
    df_uk_2011 = df_uk[df_uk['InvoiceDate'] >= '2011-01-01']
    
    # 2. Europe North (Eire, Germany, Netherlands, France)
    north_euro_countries = ['EIRE', 'Germany', 'Netherlands', 'France']
    df_euro_north = df_combined[df_combined['Country'].isin(north_euro_countries)]
    
    # 3. Europe South/West (Spain, Portugal, Switzerland, Belgium, Italy)
    south_euro_countries = ['Spain', 'Portugal', 'Switzerland', 'Belgium', 'Italy']
    df_euro_south = df_combined[df_combined['Country'].isin(south_euro_countries)]
    
    # 4. Asia & Pacific (Australia, Japan, Singapore, Hong Kong)
    asia_pac_countries = ['Australia', 'Japan', 'Singapore', 'Hong Kong']
    df_asia_pac = df_combined[df_combined['Country'].isin(asia_pac_countries)]
    
    # 5. Rest of World (USA, Canada, Channel Islands, Cyprus, Israel, etc.)
    all_specified = ['United Kingdom'] + north_euro_countries + south_euro_countries + asia_pac_countries
    df_row = df_combined[~df_combined['Country'].isin(all_specified)]

    # Define targets
    sources = {
        "legacy_uk_sales_2010.csv": df_uk_2010,
        "legacy_uk_sales_2011.csv": df_uk_2011,
        "legacy_euro_north_sales.csv": df_euro_north,
        "legacy_euro_south_sales.csv": df_euro_south,
        "legacy_asiapac_sales.csv": df_asia_pac,
        "legacy_row_sales.csv": df_row
    }

    # Save files to raw directory to act as source databases
    print("Writing legacy database simulations to 'data/raw'...")
    for filename, df_subset in sources.items():
        file_path = os.path.join(RAW_DIR, filename)
        df_subset.to_csv(file_path, index=False)
        print(f"Created: {filename} ({len(df_subset)} rows)")

    print("\nETL Source Mocking Complete! You now have 6 raw regional CSV files to run your pipeline.")

if __name__ == "__main__":
    download_dataset()
    split_and_simulate_sources()
