-- DEMO 1: Full Year Revenue Summary
-- Shows the cluster aggregating 553k rows across 3 nodes

SELECT
    COUNT(*)                        AS total_transactions,
    ROUND(SUM(revenue), 2)          AS total_revenue,
    ROUND(SUM(profit),  2)          AS total_profit,
    ROUND(AVG(profit / revenue * 100), 2) AS avg_margin_pct
FROM fact_sales;



-- DEMO 2: Revenue by Product Category
-- JOIN across distributed fact + replicated dimension

SELECT
    p.category,
    COUNT(*)                AS transactions,
    SUM(f.quantity_sold)    AS units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.profit),  2) AS total_profit
FROM fact_sales f
JOIN dim_product p ON f.dim_product_id = p.id
GROUP BY p.category
ORDER BY total_revenue DESC;



-- DEMO 3: Monthly Revenue Trend (simulated days → months)
-- Each "month" = ~30 simulated days
-- Great for showing time-series aggregation at scale

SELECT
    CEIL(simulated_day / 30.0)      AS simulated_month,
    COUNT(*)                        AS transactions,
    ROUND(SUM(revenue), 2)          AS monthly_revenue,
    ROUND(SUM(profit),  2)          AS monthly_profit
FROM fact_sales
GROUP BY simulated_month
ORDER BY simulated_month;



-- DEMO 4: Top 10 Best Selling Products

SELECT
    p.product_name,
    p.category,
    SUM(f.quantity_sold)     AS units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.dim_product_id = p.id
GROUP BY p.product_name, p.category
ORDER BY units_sold DESC
LIMIT 10;



-- DEMO 5: Rush Hour vs Non-Rush Hour Performance
-- Shows time-of-day analysis across all 365 days

SELECT
    t.is_rush_hour,
    t.part_of_day,
    COUNT(*)                 AS transactions,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(AVG(f.revenue), 2) AS avg_transaction_value
FROM fact_sales f
JOIN dim_time t ON f.dim_time_id = t.id
GROUP BY t.is_rush_hour, t.part_of_day
ORDER BY total_revenue DESC;



-- DEMO 6: Loyalty vs Walk-In Customer Spending

SELECT
    CASE WHEN c.is_loyalty THEN 'Loyalty Member' ELSE 'Walk-In' END AS customer_type,
    COUNT(DISTINCT f.dim_customer_id)   AS unique_customers,
    COUNT(*)                            AS total_transactions,
    ROUND(SUM(f.revenue), 2)            AS total_revenue,
    ROUND(AVG(f.revenue), 2)            AS avg_spend_per_transaction
FROM fact_sales f
JOIN dim_customer c ON f.dim_customer_id = c.id
GROUP BY c.is_loyalty
ORDER BY total_revenue DESC;



-- DEMO 7: Payment Method Breakdown

SELECT
    pm.method,
    COUNT(*)                 AS transactions,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(AVG(f.revenue), 2) AS avg_transaction
FROM fact_sales f
JOIN dim_payment_method pm ON f.dim_payment_method_id = pm.id
GROUP BY pm.method
ORDER BY transactions DESC;



-- DEMO 8: The Fault Tolerance Demo
-- Run this BEFORE and AFTER stopping a node with:
--   docker stop ignite-node2
-- Query should return same results both times!

SELECT
    COUNT(*)                 AS total_rows,
    ROUND(SUM(revenue), 2)   AS total_revenue
FROM fact_sales;
-- Expected: same result even with node2 stopped
-- This works because backups=1 in the schema
