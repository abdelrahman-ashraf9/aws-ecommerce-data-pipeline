-- ============================================================
-- E-COMMERCE DATA WAREHOUSE (AMAZON ATHENA DDL & ANALYTICS)
-- Bucket: aws-ecommerce-data-abdelrahman
-- Database: ecommerce_dw
-- ============================================================

-- ------------------------------------------------------------
-- 1. DATABASE CREATION
-- ------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS ecommerce_dw;


-- ------------------------------------------------------------
-- 2. DDL - DIMENSION TABLES (10 DIMENSIONS)
-- ------------------------------------------------------------

-- 1. dim_customer
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_customer (
    customer_id BIGINT,
    first_name STRING,
    last_name STRING,
    full_name STRING,
    email STRING,
    city STRING,
    country STRING,
    registration_date DATE
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_customer/';

-- 2. dim_product
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_product (
    product_id BIGINT,
    category_id BIGINT,
    product_name STRING,
    brand STRING,
    price DECIMAL(12,2),
    cost DECIMAL(12,2),
    stock INT
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_product/';

-- 3. dim_category
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_category (
    category_id BIGINT,
    category_name STRING
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_category/';

-- 4. dim_department
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_department (
    department_id BIGINT,
    department_name STRING
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_department/';

-- 5. dim_supplier
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_supplier (
    supplier_id BIGINT,
    supplier_name STRING,
    country STRING
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_supplier/';

-- 6. dim_employee
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_employee (
    employee_id BIGINT,
    manager_id BIGINT,
    department_id BIGINT,
    first_name STRING,
    last_name STRING,
    full_name STRING,
    salary DECIMAL(12,2),
    hire_date DATE
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_employee/';

-- 7. dim_shipper
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_shipper (
    shipper_id BIGINT,
    company_name STRING
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_shipper/';

-- 8. dim_date
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_date (
    date DATE,
    date_id INT,
    year INT,
    quarter INT,
    month INT,
    month_name STRING,
    day INT,
    day_of_week INT,
    day_name STRING,
    week_of_year INT
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_date/';

-- 9. dim_payment_method
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_payment_method (
    payment_method_id INT,
    payment_method STRING
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_payment_method/';

-- 10. dim_order_status
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.dim_order_status (
    order_status_id INT,
    order_status STRING
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/dim_order_status/';


-- ------------------------------------------------------------
-- 3. DDL - FACT TABLES (6 FACTS)
-- ------------------------------------------------------------

-- 1. fact_order
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.fact_order (
    order_id BIGINT,
    customer_id BIGINT,
    date_id INT,
    order_date DATE,
    order_status_id INT
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/fact_order/';

-- 2. fact_order_detail
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.fact_order_detail (
    order_detail_id BIGINT,
    order_id BIGINT,
    product_id BIGINT,
    quantity INT,
    unit_price DECIMAL(12,2),
    discount DECIMAL(12,2),
    gross_amount DECIMAL(14,2),
    discount_amount DECIMAL(14,2),
    total_amount DECIMAL(14,2)
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/fact_order_detail/';

-- 3. fact_payment
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.fact_payment (
    payment_id BIGINT,
    order_id BIGINT,
    date_id INT,
    payment_date DATE,
    payment_method_id INT,
    amount DECIMAL(14,2)
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/fact_payment/';

-- 4. fact_shipment
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.fact_shipment (
    shipment_id BIGINT,
    order_id BIGINT,
    shipper_id BIGINT,
    ship_date DATE,
    delivery_date DATE,
    shipping_days INT
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/fact_shipment/';

-- 5. fact_customer_sales
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.fact_customer_sales (
    customer_id BIGINT,
    total_orders BIGINT,
    total_quantity BIGINT,
    gross_sales DECIMAL(14,2),
    total_discount DECIMAL(14,2),
    total_sales DECIMAL(14,2),
    average_order_line DOUBLE,
    first_order_date DATE,
    last_order_date DATE,
    customer_segment STRING
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/fact_customer_sales/';

-- 6. fact_product_sales
CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_dw.fact_product_sales (
    product_id BIGINT,
    total_orders BIGINT,
    units_sold BIGINT,
    gross_sales DECIMAL(14,2),
    total_discount DECIMAL(14,2),
    total_sales DECIMAL(14,2),
    average_unit_price DOUBLE
)
STORED AS PARQUET
LOCATION 's3://aws-ecommerce-data-abdelrahman/processed/ecommerce/fact_product_sales/';


-- ------------------------------------------------------------
-- 4. PART 12 - SQL ANALYTICS & AGGREGATIONS
-- ------------------------------------------------------------

-- Task 29 & Task 34: Total Aggregates & Average Order Value (AOV)
SELECT 
    COUNT(DISTINCT fo.order_id) AS total_orders,
    COUNT(DISTINCT fo.customer_id) AS total_customers,
    COUNT(DISTINCT fd.product_id) AS total_products,
    SUM(fd.quantity) AS total_quantity_sold,
    SUM(fd.total_amount) AS total_sales,
    SUM(fd.total_amount) / COUNT(DISTINCT fo.order_id) AS average_order_value
FROM ecommerce_dw.fact_order_detail fd
JOIN ecommerce_dw.fact_order fo ON fd.order_id = fo.order_id;

-- Task 30: Monthly Sales, Orders & Quantity Performance
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT fo.order_id) AS monthly_orders,
    SUM(fd.quantity) AS monthly_quantity,
    SUM(fd.total_amount) AS monthly_sales
FROM ecommerce_dw.fact_order_detail fd
JOIN ecommerce_dw.fact_order fo ON fd.order_id = fo.order_id
JOIN ecommerce_dw.dim_date d ON fo.order_date = d.date
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- Task 31: Sales Breakdown by Category & Product
SELECT 
    c.category_name,
    p.product_name,
    SUM(fd.quantity) AS total_units_sold,
    SUM(fd.total_amount) AS total_sales
FROM ecommerce_dw.fact_order_detail fd
JOIN ecommerce_dw.dim_product p ON fd.product_id = p.product_id
JOIN ecommerce_dw.dim_category c ON p.category_id = c.category_id
GROUP BY c.category_name, p.product_name
ORDER BY total_sales DESC;

-- Task 32: Top 10 Products by Sales
SELECT 
    p.product_name,
    c.category_name,
    SUM(fd.total_amount) AS total_sales
FROM ecommerce_dw.fact_order_detail fd
JOIN ecommerce_dw.dim_product p ON fd.product_id = p.product_id
JOIN ecommerce_dw.dim_category c ON p.category_id = c.category_id
GROUP BY p.product_name, c.category_name
ORDER BY total_sales DESC
LIMIT 10;

-- Task 33: Top 10 Customers by Total Spending
SELECT 
    c.customer_id,
    c.full_name,
    c.email,
    SUM(fd.total_amount) AS total_spending
FROM ecommerce_dw.fact_order_detail fd
JOIN ecommerce_dw.fact_order fo ON fd.order_id = fo.order_id
JOIN ecommerce_dw.dim_customer c ON fo.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name, c.email
ORDER BY total_spending DESC
LIMIT 10;

-- Task 35: Order Status Breakdown
SELECT 
    os.order_status,
    COUNT(fo.order_id) AS order_count,
    SUM(fd.total_amount) AS total_order_value
FROM ecommerce_dw.fact_order fo
JOIN ecommerce_dw.dim_order_status os ON fo.order_status_id = os.order_status_id
LEFT JOIN ecommerce_dw.fact_order_detail fd ON fo.order_id = fd.order_id
GROUP BY os.order_status
ORDER BY order_count DESC;

-- Task 36: Payment Methods Analysis
SELECT 
    pm.payment_method,
    COUNT(fp.payment_id) AS number_of_transactions,
    SUM(fp.amount) AS total_payment_amount,
    ROUND(AVG(fp.amount), 2) AS average_payment_amount
FROM ecommerce_dw.fact_payment fp
JOIN ecommerce_dw.dim_payment_method pm ON fp.payment_method_id = pm.payment_method_id
GROUP BY pm.payment_method
ORDER BY total_payment_amount DESC;

-- Task 37: Shipment Performance
SELECT 
    COUNT(shipment_id) AS total_shipments,
    ROUND(AVG(shipping_days), 2) AS average_delivery_days,
    MIN(shipping_days) AS minimum_delivery_days,
    MAX(shipping_days) AS maximum_delivery_days
FROM ecommerce_dw.fact_shipment;


-- ------------------------------------------------------------
-- 5. PART 13 - ADVANCED SQL ANALYTICS (WINDOW FUNCTIONS)
-- ------------------------------------------------------------

-- Task 38: Running Cumulative Sales by Date
SELECT 
    order_date,
    daily_sales,
    SUM(daily_sales) OVER (ORDER BY order_date) AS running_cumulative_sales
FROM (
    SELECT 
        fo.order_date,
        SUM(fd.total_amount) AS daily_sales
    FROM ecommerce_dw.fact_order_detail fd
    JOIN ecommerce_dw.fact_order fo ON fd.order_id = fo.order_id
    GROUP BY fo.order_date
)
ORDER BY order_date;

-- Task 39: Month-over-Month (MoM) Growth Percentage
WITH monthly_metrics AS (
    SELECT 
        d.year,
        d.month,
        SUM(fd.total_amount) AS current_month_sales
    FROM ecommerce_dw.fact_order_detail fd
    JOIN ecommerce_dw.fact_order fo ON fd.order_id = fo.order_id
    JOIN ecommerce_dw.dim_date d ON fo.order_date = d.date
    GROUP BY d.year, d.month
)
SELECT 
    year,
    month,
    current_month_sales,
    LAG(current_month_sales) OVER (ORDER BY year, month) AS previous_month_sales,
    current_month_sales - LAG(current_month_sales) OVER (ORDER BY year, month) AS sales_difference,
    ROUND(
        (current_month_sales - LAG(current_month_sales) OVER (ORDER BY year, month)) / 
        NULLIF(LAG(current_month_sales) OVER (ORDER BY year, month), 0) * 100, 
        2
    ) AS growth_percentage
FROM monthly_metrics
ORDER BY year, month;

-- Task 40: Top 3 Ranked Products per Category
WITH ranked_category_products AS (
    SELECT 
        c.category_name,
        p.product_name,
        SUM(fd.total_amount) AS total_sales,
        DENSE_RANK() OVER (
            PARTITION BY c.category_name 
            ORDER BY SUM(fd.total_amount) DESC
        ) AS rank
    FROM ecommerce_dw.fact_order_detail fd
    JOIN ecommerce_dw.dim_product p ON fd.product_id = p.product_id
    JOIN ecommerce_dw.dim_category c ON p.category_id = c.category_id
    GROUP BY c.category_name, p.product_name
)
SELECT 
    category_name,
    product_name,
    total_sales,
    rank
FROM ranked_category_products
WHERE rank <= 3
ORDER BY category_name, rank;

-- Task 41: Customer Ranking by Spending and Order Count
SELECT 
    c.customer_id,
    c.full_name,
    SUM(fd.total_amount) AS total_spending,
    COUNT(DISTINCT fo.order_id) AS order_count,
    DENSE_RANK() OVER (ORDER BY SUM(fd.total_amount) DESC) AS customer_rank
FROM ecommerce_dw.fact_order_detail fd
JOIN ecommerce_dw.fact_order fo ON fd.order_id = fo.order_id
JOIN ecommerce_dw.dim_customer c ON fo.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY customer_rank;