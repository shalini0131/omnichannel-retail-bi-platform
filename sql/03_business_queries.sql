-- =====================================================================
-- ADVANCED BUSINESS INTELLIGENCE & ANALYTICS QUERIES (MYSQL COMPATIBLE)
-- =====================================================================

USE retail_dw;

-- 1. Net Revenue, Gross Sales, and Return Metrics
-- Summarizes high-level revenue figures, isolating return transactions.
SELECT 
    ROUND(SUM(CASE WHEN NOT is_return THEN line_total ELSE 0 END), 2) as gross_sales_gbp,
    ROUND(SUM(CASE WHEN is_return THEN line_total ELSE 0 END), 2) as returns_gbp,
    ROUND(SUM(line_total), 2) as net_sales_gbp,
    ROUND(ABS(SUM(CASE WHEN is_return THEN line_total ELSE 0 END)) * 100.0 / 
          SUM(CASE WHEN NOT is_return THEN line_total ELSE 0 END), 2) as return_rate_pct
FROM fact_sales;


-- 2. Month-over-Month (MoM) Net Revenue Growth (2010 vs 2011)
-- Uses window function LAG to compare net sales of the current month to the previous month.
WITH monthly_sales AS (
    SELECT 
        d.year,
        d.month,
        SUM(fs.line_total) as net_sales
    FROM fact_sales fs
    JOIN dim_date d ON fs.date_key = d.date_key
    GROUP BY d.year, d.month
),
growth_calc AS (
    SELECT 
        year,
        month,
        net_sales,
        LAG(net_sales, 1) OVER (ORDER BY year, month) as prev_month_sales
    FROM monthly_sales
)
SELECT 
    year,
    month,
    ROUND(net_sales, 2) as net_sales_gbp,
    ROUND(prev_month_sales, 2) as prev_month_sales_gbp,
    ROUND(((net_sales - prev_month_sales) * 100.0 / prev_month_sales), 2) as mom_growth_pct
FROM growth_calc
WHERE prev_month_sales IS NOT NULL;


-- 3. Average Order Value (AOV) and Average Basket Size (Items per Basket)
-- Evaluates transaction depth and average ticket size.
SELECT 
    COUNT(DISTINCT invoice_no) as total_orders,
    ROUND(SUM(line_total) / COUNT(DISTINCT invoice_no), 2) as average_order_value_gbp,
    ROUND(SUM(quantity) / COUNT(DISTINCT invoice_no), 2) as average_items_per_basket
FROM fact_sales
WHERE NOT is_return; -- Exclude returns to analyze purchase basket sizes accurately


-- 4. Top 10 Best Selling Products by Net Sales
-- Employs DENSE_RANK() to classify item sales performance.
WITH product_rank AS (
    SELECT 
        dp.product_code,
        dp.product_name,
        SUM(fs.line_total) as net_sales,
        SUM(fs.quantity) as total_units_sold,
        DENSE_RANK() OVER (ORDER BY SUM(fs.line_total) DESC) as sales_rank
    FROM fact_sales fs
    JOIN dim_products dp ON fs.product_code = dp.product_code
    WHERE NOT fs.is_return
    GROUP BY dp.product_code, dp.product_name
)
SELECT 
    sales_rank,
    product_code,
    product_name,
    ROUND(net_sales, 2) as net_sales_gbp,
    total_units_sold
FROM product_rank
WHERE sales_rank <= 10;


-- 5. Branch Sales Performance & Market Share Analysis
-- Measures regional performance relative to the entire retail group.
WITH branch_sales AS (
    SELECT 
        db.branch_id,
        db.branch_name,
        db.country,
        SUM(fs.line_total) as branch_net_sales
    FROM fact_sales fs
    JOIN dim_branches db ON fs.branch_id = db.branch_id
    GROUP BY db.branch_id, db.branch_name, db.country
)
SELECT 
    branch_id,
    branch_name,
    country,
    ROUND(branch_net_sales, 2) as net_sales_gbp,
    ROUND(branch_net_sales * 100.0 / (SELECT SUM(line_total) FROM fact_sales), 2) as market_share_pct
FROM branch_sales
ORDER BY branch_net_sales DESC;


-- 6. Customer Purchase Frequency (Cohort Profile)
-- Segments customer base by number of orders placed during the 2-year period.
WITH customer_order_counts AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT invoice_no) as order_count
    FROM fact_sales
    WHERE customer_id != 99999 -- Exclude guest checkouts from customer lifecycle mapping
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN order_count = 1 THEN '1. Single-purchase Customers'
        WHEN order_count BETWEEN 2 AND 5 THEN '2. Repeat Customers (2-5 orders)'
        WHEN order_count BETWEEN 6 AND 15 THEN '3. Frequent Buyers (6-15 orders)'
        ELSE '4. Power Buyers (15+ orders)'
    END as customer_segment,
    COUNT(customer_id) as customer_count,
    ROUND(COUNT(customer_id) * 100.0 / (SELECT COUNT(DISTINCT customer_id) FROM fact_sales WHERE customer_id != 99999), 2) as pct_of_customer_base
FROM customer_order_counts
GROUP BY 1
ORDER BY 1;
