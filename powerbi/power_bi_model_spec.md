# Power BI Modeling & DAX Specification

This document provides the complete, production-ready specification for building the Power BI dataset, data model, Power Query transformations, and the 20+ custom DAX measures that form the core of the Omnichannel Retail BI dashboard.

---

## 1. Data Model Architecture (Star Schema)

The data model follows a strict star schema design in Power BI Desktop. Every relationship is configured as a **1-to-Many (1:*)** join flowing from the Dimension tables to the Fact table, with **Single** cross-filter direction to maintain relational integrity and optimal query performance.

### Model Relationships:
1. **dim_date [date_key]** $\rightarrow$ **fact_sales [date_key]** (1:*)
2. **dim_customers [customer_id]** $\rightarrow$ **fact_sales [customer_id]** (1:*)
3. **dim_products [product_code]** $\rightarrow$ **fact_sales [product_code]** (1:*)
4. **dim_branches [branch_id]** $\rightarrow$ **fact_sales [branch_id]** (1:*)

---

## 2. Power Query (M Language) Data Connections

If you connect directly to PostgreSQL, use the following M script in the **Advanced Editor** for each table.

### Connection to PostgreSQL:
```powerquery
let
    Source = PostgreSQL.Database("localhost", "retail_dw"),
    dbo_fact_sales = Source{[Schema="public", Item="fact_sales"]}[Data],
    #"Removed Other Columns" = Table.SelectColumns(dbo_fact_sales, {"invoice_no", "customer_id", "product_code", "branch_id", "date_key", "transaction_time", "quantity", "unit_price", "line_total", "is_return"})
in
    #"Removed Other Columns"
```

---

## 3. Custom DAX Measures (20+ Production Formulas)

Create these measures inside a dedicated, empty measure table named `_Measures Table` to keep the model organized.

### Core Sales Measures

#### 1. Total Net Sales
```dax
Total Net Sales = SUM(fact_sales[line_total])
```
*Purpose: Total revenue generated, reflecting deductions for returns (returns are stored as negative line totals).*

#### 2. Gross Sales
```dax
Gross Sales = CALCULATE(SUM(fact_sales[line_total]), fact_sales[is_return] = FALSE)
```
*Purpose: Calculates sales value before any returns or cancellations are subtracted.*

#### 3. Total Returns Value
```dax
Total Returns Value = CALCULATE(SUM(fact_sales[line_total]), fact_sales[is_return] = TRUE)
```
*Purpose: Captures the total financial volume of refund/return transactions (represented as a negative number).*

#### 4. Return Rate %
```dax
Return Rate % = DIVIDE(ABS([Total Returns Value]), [Gross Sales], 0)
```
*Purpose: Evaluates return volume as a percentage of overall gross sales.*

#### 5. Total Transactions
```dax
Total Transactions = DISTINCTCOUNT(fact_sales[invoice_no])
```
*Purpose: Counts the total unique invoices generated.*

#### 6. Net Transaction Count
```dax
Net Transaction Count = CALCULATE(DISTINCTCOUNT(fact_sales[invoice_no]), fact_sales[is_return] = FALSE)
```
*Purpose: Counts unique purchase invoices, excluding returns.*

---

### Profitability & Margin Measures

#### 7. Gross Profit (Estimated)
```dax
Gross Profit = [Total Net Sales] * 0.40
```
*Purpose: Assuming a standard 40% retail markup margin, this estimates gross margin dollars.*

#### 8. Estimated Gross Margin %
```dax
Estimated Gross Margin % = DIVIDE([Gross Profit], [Total Net Sales], 0)
```
*Purpose: Tracks gross margin performance.*

---

### Transaction Metrics (AOV & Basket Size)

#### 9. Average Order Value (AOV)
```dax
Average Order Value (AOV) = DIVIDE([Gross Sales], [Net Transaction Count], 0)
```
*Purpose: Tracks the average amount spent per purchase transaction.*

#### 10. Average Items Per Basket (Basket Size)
```dax
Average Items Per Basket = DIVIDE(SUM(fact_sales[quantity]), [Net Transaction Count], 0)
```
*Purpose: Measures average number of items purchased per checkout.*

---

### Time-Intelligence & Growth Measures

#### 11. Net Sales (Previous Month)
```dax
Net Sales PM = CALCULATE([Total Net Sales], PREVIOUSMONTH(dim_date[date]))
```
*Purpose: Shifts net sales back by one month to calculate MoM growth.*

#### 12. Month-over-Month (MoM) Growth
```dax
Sales MoM Growth % = DIVIDE([Total Net Sales] - [Net Sales PM], [Net Sales PM], 0)
```
*Purpose: Growth percentage compared to the previous calendar month.*

#### 13. Same-Store Sales Growth (SSSG) %
```dax
Same-Store Sales Growth % = 
VAR SalesLY = CALCULATE([Total Net Sales], SAMEPERIODLASTYEAR(dim_date[date]))
RETURN
DIVIDE([Total Net Sales] - SalesLY, SalesLY, 0)
```
*Purpose: True brick-and-mortar retail performance index tracking yearly change in established outlets.*

#### 14. Year-to-Date (YTD) Sales
```dax
Sales YTD = TOTALYTD([Total Net Sales], dim_date[date])
```
*Purpose: Running sales total starting from January 1st of the active calendar year.*

#### 15. Prior Year YTD Sales
```dax
Sales LY YTD = CALCULATE([Sales YTD], SAMEPERIODLASTYEAR(dim_date[date]))
```
*Purpose: Historical benchmark to track current year YTD progress.*

#### 16. Year-over-Year (YoY) Growth %
```dax
Sales YoY Growth % = DIVIDE([Sales YTD] - [Sales LY YTD], [Sales LY YTD], 0)
```
*Purpose: Compares running year performance relative to previous year.*

---

### Customer & Cohort Metrics

#### 17. Active Customers Count
```dax
Active Customers Count = CALCULATE(DISTINCTCOUNT(fact_sales[customer_id]), fact_sales[customer_id] <> 99999)
```
*Purpose: Tracks unique non-guest customer profiles interacting with the brand.*

#### 18. Customer Retention Rate %
```dax
Customer Retention Rate % = 
VAR CustomersThisMonth = VALUES(fact_sales[customer_id])
VAR PreviousMonthDate = PREVIOUSMONTH(dim_date[date])
VAR CustomersLastMonth = CALCULATE(VALUES(fact_sales[customer_id]), PreviousMonthDate, fact_sales[customer_id] <> 99999)
VAR RetainedCustomers = INTERSECT(CustomersThisMonth, CustomersLastMonth)
RETURN
DIVIDE(COUNTROWS(RetainedCustomers), COUNTROWS(CustomersLastMonth), 0)
```
*Purpose: Computes month-over-month repeat buyer preservation.*

#### 19. Average Customer Lifetime Value (CLV)
```dax
Average CLV = DIVIDE([Total Net Sales], [Active Customers Count], 0)
```
*Purpose: Evaluates average value generated per registered customer profile.*

---

### Advanced Contextual Measures (What-If Parameters)

#### 20. Target Sales Projection (What-If Simulation)
```dax
Simulated Target Sales = [Total Net Sales] * (1 + [Growth Parameter Value])
```
*Purpose: Uses a Power BI decimal parameter slider (`Growth Parameter`) to dynamically project target sales.*

---

## 4. Visual Layout Specifications

### Page 1: Executive KPI Overview
* **Cards (Top):** Net Sales (£), Total Transactions, Average Order Value (AOV), Return Rate (%).
* **Line Chart:** Monthly Sales trend line (Year-over-Year comparison overlay).
* **Donut Chart:** Market Share (%) by Branch Region.
* **Map:** Geographical bubbles showing country-level sales distribution.
* **Slicers:** Date Range (Relative Slider), Branch Country (Drop-down).

### Page 2: Product & Inventory Performance
* **Bar Chart:** Top 10 Products by Net Sales (horizontal bars, color gradient based on total units).
* **Matrix Visual:** Product Categories by Sales, Return Rate, and Profit Margin.
* **Scatter Plot:** Price vs Quantity sold, helping identify price elasticity per product segment.

### Page 3: Marketing & Customer Cohorts
* **Column Chart:** Monthly Cohort Retention Rates.
* **Stacked Bar Chart:** Registered vs Guest customer revenue contributions.
* **Card KPI:** Average Customer Lifetime Value (CLV).
