-- =====================================================================
-- DATA AUDITING & CLEANING QUERIES (MYSQL COMPATIBLE)
-- =====================================================================

USE retail_dw;

-- 1. Identify Duplicate Rows in Legacy Stage (if any existed before ETL cleaning)
-- Uses ROW_NUMBER() over keys to find duplicate entries
WITH duplicate_audit AS (
    SELECT 
        invoice_no, 
        product_code, 
        date_key, 
        quantity, 
        unit_price,
        ROW_NUMBER() OVER (
            PARTITION BY invoice_no, product_code, date_key, quantity, unit_price 
            ORDER BY sales_id
        ) as row_num
    FROM fact_sales
)
SELECT * 
FROM duplicate_audit 
WHERE row_num > 1
LIMIT 100;

-- 2. Audit Missing Customer IDs (Guest checkouts)
-- Verifies our guest profile placeholder logic (99999 ID map)
SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(line_total) as total_spent,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_sales), 2) as pct_of_total_rows
FROM fact_sales
WHERE customer_id = 99999
GROUP BY customer_id;

-- 3. Verify Referential Integrity (Checking for Orphan Rows)
-- Ensures all fact records map correctly to dimensions
SELECT 
    COUNT(fs.sales_id) as total_fact_rows,
    COUNT(dc.customer_id) as matching_customers,
    COUNT(dp.product_code) as matching_products,
    COUNT(db.branch_id) as matching_branches,
    COUNT(dd.date_key) as matching_dates
FROM fact_sales fs
LEFT JOIN dim_customers dc ON fs.customer_id = dc.customer_id
LEFT JOIN dim_products dp ON fs.product_code = dp.product_code
LEFT JOIN dim_branches db ON fs.branch_id = db.branch_id
LEFT JOIN dim_date dd ON fs.date_key = dd.date_key;

-- 4. Check for anomalies (negative quantities without returns, negative unit prices)
-- Ensure returns are correctly flagged
SELECT 
    invoice_no, 
    quantity, 
    is_return
FROM fact_sales
WHERE quantity < 0 AND is_return = FALSE;

-- Ensure no negative unit prices exist
SELECT 
    COUNT(*) as anomaly_count
FROM fact_sales
WHERE unit_price < 0;
