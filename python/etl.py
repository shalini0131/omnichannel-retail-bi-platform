import os
import pandas as pd
import numpy as np
import mysql.connector

# Database Connection Settings (Override via env variables if needed)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "retail_dw")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "#Shalini12345")  # Provide your MySQL password here
DB_PORT = os.getenv("DB_PORT", "3306")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def get_db_connection():
    """Establishes connection to MySQL database."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

def extract_raw_sources():
    """Extracts and concatenates the 6 legacy raw CSV source files."""
    source_files = [
        "legacy_uk_sales_2010.csv",
        "legacy_uk_sales_2011.csv",
        "legacy_euro_north_sales.csv",
        "legacy_euro_south_sales.csv",
        "legacy_asiapac_sales.csv",
        "legacy_row_sales.csv"
    ]
    
    dfs = []
    print("Extracting raw legacy files...")
    for file in source_files:
        file_path = os.path.join(RAW_DIR, file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file {file_path} not found. Run split_raw_data.py first.")
        df = pd.read_csv(file_path)
        print(f"Read: {file} ({len(df)} rows)")
        dfs.append(df)
        
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"Total Extracted Rows: {len(combined_df)}")
    return combined_df

def transform_data(df):
    """Cleans and structures the data into relational dimension and fact dataframes."""
    print("Transforming data...")
    
    # 1. Clean Column Names & Types
    df.columns = [c.strip() for c in df.columns]
    
    # Cast InvoiceDate to datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Clean Description
    df['Description'] = df['Description'].str.strip()
    df['Description'] = df['Description'].fillna("UNKNOWN PRODUCT")
    
    # Clean StockCode
    df['StockCode'] = df['StockCode'].astype(str).str.strip().str.upper()
    df['StockCode'] = df['StockCode'].fillna("UNKNOWN")
    
    # Fill missing Customer IDs with a standard Guest ID (99999) to prevent loss of transaction revenue
    df['Customer ID'] = df['Customer ID'].fillna(99999).astype(int)
    
    # Remove records with zero or negative prices
    initial_len = len(df)
    df = df[df['Price'] > 0]
    print(f"Removed {initial_len - len(df)} records with Price <= 0")
    
    # Remove records with zero quantities
    initial_len = len(df)
    df = df[df['Quantity'] != 0]
    print(f"Removed {initial_len - len(df)} records with Quantity = 0")
    
    # Identify return/cancellation transactions (Invoices starting with 'C')
    df['is_return'] = df['Invoice'].astype(str).str.startswith('C')
    
    # Calculate Line Amount
    df['line_total'] = df['Quantity'] * df['Price']
    
    # Save the cleaned flat file to processed folder for secondary analysis
    cleaned_path = os.path.join(PROCESSED_DIR, "cleaned_transactions.csv")
    df.to_csv(cleaned_path, index=False)
    print(f"Saved cleaned records to: {cleaned_path}")
    
    # ---- CREATE DIMENSIONS ----
    
    # A. Dim Customers
    customer_country = df.sort_values('InvoiceDate').groupby('Customer ID')['Country'].last().reset_index()
    dim_customers = pd.DataFrame({
        'customer_id': customer_country['Customer ID'],
        'country': customer_country['Country']
    })
    
    # B. Dim Products
    product_desc = df.groupby('StockCode')['Description'].agg(lambda x: x.mode()[0] if not x.mode().empty else "UNKNOWN").reset_index()
    dim_products = pd.DataFrame({
        'product_code': product_desc['StockCode'],
        'product_name': product_desc['Description']
    })
    
    # C. Dim Branches
    unique_countries = df['Country'].unique()
    dim_branches = []
    for idx, country in enumerate(unique_countries, 1):
        if country == 'United Kingdom':
            region = 'UK'
        elif country in ['EIRE', 'Germany', 'Netherlands', 'France', 'Belgium', 'Switzerland', 'Spain', 'Portugal', 'Italy']:
            region = 'EUROPE'
        elif country in ['Australia', 'Japan', 'Singapore', 'Hong Kong']:
            region = 'ASIA_PAC'
        else:
            region = 'REST_OF_WORLD'
        dim_branches.append({'branch_id': idx, 'branch_name': f"Branch_{region}_{country.replace(' ', '_')}", 'country': country})
    dim_branches = pd.DataFrame(dim_branches)
    
    # D. Dim Date
    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()
    date_range = pd.date_range(start=min_date, end=max_date)
    dim_date = pd.DataFrame({
        'date_key': date_range.strftime('%Y%m%d').astype(int),
        'date': date_range.date,
        'year': date_range.year,
        'quarter': date_range.quarter,
        'month': date_range.month,
        'day': date_range.day,
        'day_of_week': date_range.dayofweek + 1,
        'is_weekend': date_range.dayofweek.isin([5, 6]).astype(int)
    })
    
    # E. Fact Sales
    df_fact = df.merge(dim_branches, left_on='Country', right_on='country', how='left')
    df_fact['date_key'] = df_fact['InvoiceDate'].dt.strftime('%Y%m%d').astype(int)
    
    # Convert is_return to 1/0 for MySQL compatibility
    df_fact['is_return'] = df_fact['is_return'].astype(int)
    
    # Format transaction time as string HH:MM:SS
    df_fact['transaction_time'] = df_fact['InvoiceDate'].dt.strftime('%H:%M:%S')
    
    fact_sales = pd.DataFrame({
        'invoice_no': df_fact['Invoice'].astype(str),
        'customer_id': df_fact['Customer ID'],
        'product_code': df_fact['StockCode'],
        'branch_id': df_fact['branch_id'],
        'date_key': df_fact['date_key'],
        'transaction_time': df_fact['transaction_time'],
        'quantity': df_fact['Quantity'],
        'unit_price': df_fact['Price'],
        'line_total': df_fact['line_total'],
        'is_return': df_fact['is_return']
    })
    
    return dim_customers, dim_products, dim_branches, dim_date, fact_sales

def bulk_load_to_db(conn, df, table_name, columns):
    """Performs bulk database loads into MySQL using executemany in batched chunks."""
    cursor = conn.cursor()
    
    # Clean NaN values to None for proper SQL NULL insertions
    df_clean = df.replace({np.nan: None})
    
    # Build the INSERT statement
    cols_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    if table_name.startswith("dim_"):
        query = f"INSERT IGNORE INTO {table_name} ({cols_str}) VALUES ({placeholders})"
    else:
        query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
    
    # Disable autocommit to speed up batch transaction processing
    conn.autocommit = False
    
    # Convert dataframe values to a list of tuples
    data_tuples = [tuple(x) for x in df_clean.values]
    
    # Truncate table (deletes existing keys, cascading relationships must be handled carefully)
    print(f"Truncating table {table_name}...")
    try:
        cursor.execute(f"SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute(f"TRUNCATE TABLE {table_name};")
        cursor.execute(f"SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error truncating table {table_name}: {e}")
        cursor.close()
        raise e
        
    print(f"Loading {len(df)} rows into {table_name}...")
    try:
        # Load in batch chunks of 50,000 records to prevent memory limits
        chunk_size = 50000
        for i in range(0, len(data_tuples), chunk_size):
            chunk = data_tuples[i:i+chunk_size]
            cursor.executemany(query, chunk)
        conn.commit()
        print("Loaded successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error loading data: {e}")
        raise e
    finally:
        cursor.close()

def main():
    # 1. Extract
    df_raw = extract_raw_sources()
    
    # 2. Transform
    dim_cust, dim_prod, dim_br, dim_dt, fact_sl = transform_data(df_raw)
    
    # 3. Load
    print("\nConnecting to MySQL Server for database load...")
    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Please check that MySQL Server is running, database 'retail_dw' exists,")
        print("and the user 'root' and password match your configuration.")
        return
        
    try:
        # Load dimensions first
        bulk_load_to_db(conn, dim_dt, 'dim_date', ('date_key', 'date', 'year', 'quarter', 'month', 'day', 'day_of_week', 'is_weekend'))
        bulk_load_to_db(conn, dim_cust, 'dim_customers', ('customer_id', 'country'))
        bulk_load_to_db(conn, dim_prod, 'dim_products', ('product_code', 'product_name'))
        bulk_load_to_db(conn, dim_br, 'dim_branches', ('branch_id', 'branch_name', 'country'))
        
        # Load fact table last
        bulk_load_to_db(conn, fact_sl, 'fact_sales', 
                        ('invoice_no', 'customer_id', 'product_code', 'branch_id', 'date_key', 'transaction_time', 'quantity', 'unit_price', 'line_total', 'is_return'))
        print("\nAll MySQL tables loaded successfully!")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
