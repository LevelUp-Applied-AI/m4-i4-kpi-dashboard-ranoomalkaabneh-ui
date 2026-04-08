# KPI Framework — Amman Digital Market

Define 5 KPIs for the Amman Digital Market. At least 2 must be time-based and 1 must be cohort-based.

---

## KPI 1

- **Name:**Total Net Revenue
- **Definition**: The total revenue generated from all   completed (non-cancelled) orders.
   **Formula**:Sum(quantity × unit_price)
    **Data Source** (tables/columns):
      order_items (quantity), products (unit_price), orders (status)
    **Baseline Value**: 48,701.50
    **Interpretation*:The marketplace generated 48.7K in revenue over the observed period, representing the overall business scale after excluding cancelled orders and invalid quantities.

---

## KPI 2

- **Name:**Monthly Revenue Trend
- **Definition:**Total revenue generated each month to track growth patterns over time
- **Formula:**Sum(quantity × unit_price) grouped by order_month
- **Data Source (tables/columns):**orders (order_date), order_items (quantity), products (unit_price)
- **Baseline Value:**Peak = June 2025 → 5,086.5
- **Interpretation:**Revenue is not stable over time and shows significant spikes, particularly in March and June 2025, indicating periods of increased demand or successful campaigns.

---

## KPI 3

- **Name:**Monthly Order Volume
- **Definition:**Number of completed orders per month
- **Formula:**Count(order_id) grouped by order_month
- **Data Source (tables/columns):**orders (order_id, order_date, status)Peak = June 2025 → 47 orders
- **Interpretation:**Order volume remains relatively stable around 21–23 orders per month, but sharp increases (e.g., March and June 2025) drive revenue spikes, indicating demand surges.

---

## KPI 4

- **Name:**Average Order Value (AOV)
- **Definition:**The average revenue generated per order
- **Formula:**Total Revenue ÷ Number of Orders
- **Data Source (tables/columns):**order_items (quantity), products (unit_price), orders (order_id)
- **Baseline Value:**109.43
- **Interpretation:**On average, each order generates about 109 in revenue, indicating moderate basket size and serving as a key metric for pricing and upselling strategies.

---

## KPI 5

- **Name:**Revenue by Customer City
- **Definition:**Total revenue contribution segmented by customer location (city)
- **Formula:**Sum(quantity × unit_price) grouped by city
- **Data Source (tables/columns):**customers (city), orders (customer_id), order_items, products
- **Baseline Value:**Amman = 15,719.0 (highest), Irbid = 7,250.5
- **Interpretation:**Revenue is highly concentrated in Amman, which generates more than double the revenue of Irbid. However, a large portion of revenue (7,554.5) is associated with unknown city values, indicating a data quality issue that may affect geographic analysis.
