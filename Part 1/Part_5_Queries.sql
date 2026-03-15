--Query 1: Monthly Sales Summary
SELECT month_name, year, COUNT(sale_key) AS total_orders, SUM(total_price) AS total_revenue
FROM fact_sales
JOIN dim_date ON fact_sales.date_key = dim_date.date_key
GROUP BY year, month, month_name
ORDER BY year, month;

--Query 2: Top Customers by Spending
SELECT first_name, last_name, COUNT(sale_key) AS total_orders, SUM(total_price) AS total_spent
FROM fact_sales
JOIN dim_customer ON fact_sales.customer_key = dim_customer.customer_key
GROUP BY dim_customer.customer_key, first_name, last_name
ORDER BY total_spent DESC;

--Query 3: Revenue by Product Category and Month
SELECT category, month_name, SUM(total_price) AS total_revenue
FROM fact_sales
JOIN dim_product ON fact_sales.product_key = dim_product.product_key
JOIN dim_date ON fact_sales.date_key = dim_date.date_key
GROUP BY category, month, month_name
ORDER BY category, month;