-- name: monthly_revenue
SELECT month, ROUND(SUM(line_total), 2) AS revenue, COUNT(DISTINCT order_id) AS orders
FROM orders_clean WHERE status = 'completed'
GROUP BY month ORDER BY month;

-- name: revenue_by_category
SELECT category, ROUND(SUM(line_total), 2) AS revenue,
       ROUND(100.0 * SUM(line_total) / (SELECT SUM(line_total) FROM orders_clean WHERE status = 'completed'), 1) AS pct_of_revenue
FROM orders_clean WHERE status = 'completed'
GROUP BY category ORDER BY revenue DESC;

-- name: top_products
SELECT product_name, category, SUM(quantity) AS units, ROUND(SUM(line_total), 2) AS revenue
FROM orders_clean WHERE status = 'completed'
GROUP BY product_name, category ORDER BY revenue DESC LIMIT 5;

-- name: revenue_by_country
SELECT country, ROUND(SUM(line_total), 2) AS revenue, COUNT(DISTINCT customer_id) AS customers
FROM orders_clean WHERE status = 'completed'
GROUP BY country ORDER BY revenue DESC;

-- name: return_and_cancel_rate
SELECT status, COUNT(DISTINCT order_id) AS orders,
       ROUND(100.0 * COUNT(DISTINCT order_id) / (SELECT COUNT(DISTINCT order_id) FROM orders_clean), 1) AS pct_of_orders
FROM orders_clean GROUP BY status ORDER BY orders DESC;

-- name: top_customers
SELECT customer_id, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(line_total), 2) AS revenue
FROM orders_clean WHERE status = 'completed'
GROUP BY customer_id ORDER BY revenue DESC LIMIT 10;
