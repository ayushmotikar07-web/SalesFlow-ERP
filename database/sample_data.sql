-- SalesFlow ERP Sample Data
-- Run create_users.py first to create Admin and Sales accounts.

INSERT INTO customers
(customer_name, email, phone, address, is_active)
VALUES
('ABC Technologies', 'abc@example.com', '9876543210', 'Nagpur', TRUE),
('Bright Solutions', 'bright@example.com', '9876543211', 'Pune', TRUE),
('Global Enterprises', 'global@example.com', '9876543212', 'Mumbai', TRUE);

INSERT INTO products
(product_code, product_name, category, price, stock_quantity, status)
VALUES
('PRD-001', 'Wireless Mouse', 'Electronics', 599.00, 50, 'Active'),
('PRD-002', 'USB Keyboard', 'Electronics', 899.00, 30, 'Active'),
('PRD-003', 'Laptop Stand', 'Accessories', 749.00, 20, 'Active');