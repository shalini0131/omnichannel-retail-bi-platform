# KPI Definitions — Retail Business Intelligence

This document defines the mathematical equations and business logic used to track key indicators in the Power BI dashboard and SQL reports.

---

## 1. Financial KPIs

### Net Revenue
The total net billing value generated from transactions, accounting for returns.
$$\text{Net Revenue} = \sum (\text{Line Total}) = \sum (\text{Quantity} \times \text{Unit Price})$$
*Note: Returns are recorded as negative line totals, meaning they subtract from this total automatically.*

### Gross Sales
The total gross sales generated before return deductions are applied.
$$\text{Gross Sales} = \sum (\text{Line Total}) \quad \text{where} \quad \text{is\_return} = \text{FALSE}$$

### Returns Value
The total monetary volume of returns/refunds processed.
$$\text{Returns Value} = \sum (\text{Line Total}) \quad \text{where} \quad \text{is\_return} = \text{TRUE}$$

### Return Rate %
Measures return volume relative to gross sales. High return rates signal quality issues or customer dissatisfaction.
$$\text{Return Rate \%} = \frac{|\text{Returns Value}|}{\text{Gross Sales}} \times 100$$

### Estimated Gross Margin %
Tracks general profitability assuming a standard retail markup cost-of-goods-sold (COGS) model of 60% of sales (meaning a 40% margin).
$$\text{Gross Profit} = \text{Net Revenue} \times 0.40$$
$$\text{Estimated Gross Margin \%} = \frac{\text{Gross Profit}}{\text{Net Revenue}} \times 100 = 40.0\%$$

---

## 2. Customer & Transaction Metrics

### Average Order Value (AOV)
The average spending rate per purchase transaction. Used to track shifts in customer purchasing power or effectiveness of cross-selling.
$$\text{AOV} = \frac{\text{Gross Sales}}{\text{Unique Purchase Invoices}}$$

### Average Basket Size (Items per Basket)
The average number of units checked out in a single invoice.
$$\text{Average Basket Size} = \frac{\sum (\text{Quantity})}{\text{Unique Purchase Invoices}} \quad \text{where} \quad \text{is\_return} = \text{FALSE}$$

### Same-Store Sales Growth (SSSG) %
Measures sales performance of established retail channels over a comparable historical timeline.
$$\text{SSSG \%} = \frac{\text{Net Sales}_{\text{Current Period}} - \text{Net Sales}_{\text{Same Period Last Year}}}{\text{Net Sales}_{\text{Same Period Last Year}}} \times 100$$

### Customer Retention Rate %
Evaluates what percentage of active buyers returned to make another purchase in the subsequent month.
$$\text{Retention Rate \%} = \frac{\text{Customers}_{\text{Current Month}} \cap \text{Customers}_{\text{Previous Month}}}{\text{Customers}_{\text{Previous Month}}} \times 100$$
*Note: Guest checkouts (`99999`) are excluded from customer cohort calculations to maintain validity.*
