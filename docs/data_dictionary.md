# Data Dictionary — Omnichannel Retail Data Warehouse

This dictionary defines the tables and attributes contained in the relational Star Schema of the `retail_dw` database.

---

## 1. Table: `dim_date`
Contains pre-calculated calendar dates and attributes to support efficient time-intelligence calculations without on-the-fly parsing.

| Column Name | Data Type | Primary/Foreign Key | Description / Range | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `date_key` | `INT` | Primary Key | Format: YYYYMMDD | `20101115` |
| `date` | `DATE` | Unique Constraint | Actual calendar date | `2010-11-15` |
| `year` | `INT` | - | Four-digit calendar year | `2010` |
| `quarter` | `INT` | - | Calendar quarter (1 to 4) | `4` |
| `month` | `INT` | - | Calendar month (1 to 12) | `11` |
| `day` | `INT` | - | Day of the month (1 to 31) | `15` |
| `day_of_week` | `INT` | - | Day index (1 = Monday, 7 = Sunday) | `1` (Monday) |
| `is_weekend` | `INT` | - | Weekend indicator (0 = Weekday, 1 = Weekend) | `0` |

---

## 2. Table: `dim_customers`
Provides descriptive profiles of customer accounts.

| Column Name | Data Type | Primary/Foreign Key | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `customer_id` | `INT` | Primary Key | Unique customer ID. Guest checkouts are mapped to `99999`. | `17850` |
| `country` | `VARCHAR(100)` | - | Country of billing/shipping address. | `United Kingdom` |

---

## 3. Table: `dim_products`
Captures catalog details for distinct retail SKUs.

| Column Name | Data Type | Primary/Foreign Key | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `product_code` | `VARCHAR(50)` | Primary Key | Unique stock identifier (StockCode). | `85123A` |
| `product_name` | `VARCHAR(255)` | - | Description of the product item. | `WHITE HANGING HEART T-LIGHT HOLDER` |

---

## 4. Table: `dim_branches`
Maps transactions to geographical operations and administrative structures.

| Column Name | Data Type | Primary/Foreign Key | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `branch_id` | `INT` | Primary Key | Auto-incrementing identifier. | `1` |
| `branch_name` | `VARCHAR(100)` | - | Generated name of the regional operations group. | `Branch_UK_United_Kingdom` |
| `country` | `VARCHAR(100)` | Unique Constraint | Country associated with the branch. | `United Kingdom` |

---

## 5. Table: `fact_sales`
The central transaction table recording individual line-item invoice entries.

| Column Name | Data Type | Primary/Foreign Key | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `sales_id` | `SERIAL` | Primary Key | Auto-incrementing unique index. | `14562` |
| `invoice_no` | `VARCHAR(50)` | - | 6-digit transaction identifier. Starts with `C` if returning items. | `536365` |
| `customer_id` | `INT` | Foreign Key $\rightarrow$ `dim_customers` | Links transaction line to customer. | `17850` |
| `product_code` | `VARCHAR(50)` | Foreign Key $\rightarrow$ `dim_products` | Links transaction line to product catalog. | `85123A` |
| `branch_id` | `INT` | Foreign Key $\rightarrow$ `dim_branches` | Links transaction line to regional branch. | `1` |
| `date_key` | `INT` | Foreign Key $\rightarrow$ `dim_date` | Links transaction line to calendar day. | `20101201` |
| `transaction_time` | `TIME` | - | Time of invoice printing (HH:MM:SS). | `08:26:00` |
| `quantity` | `INT` | - | Number of units purchased (negative values represent returns). | `6` |
| `unit_price` | `DECIMAL(10,2)` | - | Price per individual product unit in GBP (£). | `2.55` |
| `line_total` | `DECIMAL(12,2)` | - | Calculated row total: `quantity * unit_price`. | `15.30` |
| `is_return` | `BOOLEAN` | - | Flag indicating if this row represents a return/refund. | `FALSE` |
