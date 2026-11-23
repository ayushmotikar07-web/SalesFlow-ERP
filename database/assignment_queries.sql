-- 1. Top 3 customers by confirmed sales value
SELECT
    c.id,
    c.customer_name,
    SUM(so.grand_total) AS total_sales
FROM customers c
JOIN sales_orders so ON so.customer_id = c.id
WHERE so.status = 'Confirmed'
GROUP BY c.id, c.customer_name
ORDER BY total_sales DESC
LIMIT 3;


-- 2. Top 3 products by confirmed quantity sold
SELECT
    p.id,
    p.product_code,
    p.product_name,
    SUM(soi.quantity) AS total_quantity_sold
FROM products p
JOIN sales_order_items soi ON soi.product_id = p.id
JOIN sales_orders so ON so.id = soi.sales_order_id
WHERE so.status = 'Confirmed'
GROUP BY p.id, p.product_code, p.product_name
ORDER BY total_quantity_sold DESC
LIMIT 3;


-- 3. Customers who have never placed an order
SELECT
    c.id,
    c.customer_name,
    c.email,
    c.phone
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM sales_orders so
    WHERE so.customer_id = c.id
);


-- 4. Month-wise confirmed sales by year and month
SELECT
    YEAR(order_date) AS sales_year,
    MONTH(order_date) AS sales_month,
    SUM(grand_total) AS total_sales
FROM sales_orders
WHERE status = 'Confirmed'
GROUP BY YEAR(order_date), MONTH(order_date)
ORDER BY sales_year, sales_month;


-- 5. Products below a supplied stock threshold
-- Change 10 to the required threshold.
SET @stock_threshold = 10;

SELECT
    id,
    product_code,
    product_name,
    stock_quantity
FROM products
WHERE stock_quantity < @stock_threshold
ORDER BY stock_quantity ASC;
