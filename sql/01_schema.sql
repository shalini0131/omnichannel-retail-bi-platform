-- =====================================================================
-- DATABASE SCHEMA SETUP: OMNICHANNEL RETAIL DATA WAREHOUSE (STAR SCHEMA)
-- =====================================================================

-- Run this file in MySQL Server to create the schema before executing the Python ETL.
-- If creating database from scratch:
-- CREATE DATABASE retail_dw;
-- USE retail_dw;

-- ---------------------------------------------------------------------
-- 1. DIMENSION TABLES
-- ---------------------------------------------------------------------

-- A. Date Dimension (Pre-populated calendar helper)
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,              -- Format: YYYYMMDD
    date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    day_of_week INT NOT NULL,              -- 1 = Monday, 7 = Sunday
    is_weekend INT NOT NULL                -- 0 = Weekday, 1 = Weekend
);

-- B. Customer Dimension
CREATE TABLE dim_customers (
    customer_id INT PRIMARY KEY,           -- Matches Customer ID in CSV (99999 for Guest checkouts)
    country VARCHAR(100) NOT NULL
);

-- C. Product Dimension
CREATE TABLE dim_products (
    product_code VARCHAR(50) PRIMARY KEY,  -- StockCode
    product_name VARCHAR(255) NOT NULL     -- Description
);

-- D. Branch/Region Dimension
CREATE TABLE dim_branches (
    branch_id INT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    CONSTRAINT uq_country UNIQUE (country)
);

-- ---------------------------------------------------------------------
-- 2. FACT TABLE
-- ---------------------------------------------------------------------

CREATE TABLE fact_sales (
    sales_id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_no VARCHAR(50) NOT NULL,
    customer_id INT,
    product_code VARCHAR(50),
    branch_id INT,
    date_key INT,
    transaction_time TIME NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(12, 2) NOT NULL,
    is_return BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_code) REFERENCES dim_products(product_code),
    FOREIGN KEY (branch_id) REFERENCES dim_branches(branch_id),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- ---------------------------------------------------------------------
-- 3. INDEXES FOR QUERY OPTIMIZATION
-- ---------------------------------------------------------------------

-- Create indexes on Foreign Keys to optimize star join queries and aggregations
CREATE INDEX idx_sales_customer ON fact_sales(customer_id);
CREATE INDEX idx_sales_product ON fact_sales(product_code);
CREATE INDEX idx_sales_branch ON fact_sales(branch_id);
CREATE INDEX idx_sales_date ON fact_sales(date_key);
CREATE INDEX idx_sales_invoice ON fact_sales(invoice_no);

-- Composite index to speed up daily sales summaries and time-series reports
CREATE INDEX idx_sales_date_amount ON fact_sales(date_key, line_total);
