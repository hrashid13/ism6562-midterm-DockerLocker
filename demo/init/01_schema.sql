-- ============================================================
-- GROCERY STORE SIMULATION - OLAP SCHEMA
-- Apache Ignite 2 - Star Schema
--
-- REPLICATED  = small dimension tables (copied to all nodes)
-- PARTITIONED = large fact table (split across nodes)
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_time (
    id              INT PRIMARY KEY,
    simulated_day   INT NOT NULL,
    hour_of_day     INT NOT NULL,
    time_label      VARCHAR(20),
    part_of_day     VARCHAR(20),
    is_rush_hour    BOOLEAN
) WITH "template=replicated";

CREATE TABLE IF NOT EXISTS dim_product (
    id              INT PRIMARY KEY,
    source_id       INT NOT NULL,
    product_name    VARCHAR(150) NOT NULL,
    category        VARCHAR(50)  NOT NULL,
    subcategory     VARCHAR(50),
    unit_cost       DECIMAL(8,2)
) WITH "template=replicated";

CREATE TABLE IF NOT EXISTS dim_customer (
    id              INT PRIMARY KEY,
    source_id       INT NOT NULL,
    customer_name   VARCHAR(100),
    is_loyalty      BOOLEAN,
    join_date       DATE
) WITH "template=replicated";

CREATE TABLE IF NOT EXISTS dim_employee (
    id              INT PRIMARY KEY,
    source_id       INT NOT NULL,
    employee_name   VARCHAR(100),
    emp_role        VARCHAR(50)
) WITH "template=replicated";

CREATE TABLE IF NOT EXISTS dim_payment_method (
    id              INT PRIMARY KEY,
    method          VARCHAR(20) NOT NULL
) WITH "template=replicated";

CREATE TABLE IF NOT EXISTS fact_sales (
    id                      INT PRIMARY KEY,
    dim_time_id             INT NOT NULL,
    dim_product_id          INT NOT NULL,
    dim_customer_id         INT NOT NULL,
    dim_employee_id         INT,
    dim_payment_method_id   INT NOT NULL,
    source_transaction_id   INT NOT NULL,
    simulated_day           INT NOT NULL,
    quantity_sold           INT NOT NULL,
    unit_price              DECIMAL(8,2)  NOT NULL,
    unit_cost               DECIMAL(8,2)  NOT NULL,
    revenue                 DECIMAL(10,2) NOT NULL,
    cost                    DECIMAL(10,2) NOT NULL,
    profit                  DECIMAL(10,2) NOT NULL
) WITH "template=partitioned,backups=1";

CREATE INDEX IF NOT EXISTS idx_fact_day     ON fact_sales(simulated_day);
CREATE INDEX IF NOT EXISTS idx_fact_product ON fact_sales(dim_product_id);
CREATE INDEX IF NOT EXISTS idx_fact_time    ON fact_sales(dim_time_id);
