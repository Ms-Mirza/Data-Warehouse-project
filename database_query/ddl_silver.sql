/*
===============================================================================
DDL Script: Create Silver Tables -- MySQL version
===============================================================================
Purpose:
    Creates the cleansed/standardized tables in the 'silver' database.

Added for analytics / ML performance (not in the original):
    - Indexes on the columns the Gold views JOIN and FILTER on
      (cst_id, cst_key, prd_key, cat_id, sls_cust_id, sls_prd_key, order dates).
      SQL Server's clustered index behavior gave some of this "for free";
      MySQL/InnoDB tables need explicit secondary indexes or these joins will
      full-scan as the tables grow, which matters once you're pulling
      training data or doing repeated feature extraction from Gold.
===============================================================================
*/

DROP TABLE IF EXISTS silver.crm_cust_info;

CREATE TABLE silver.crm_cust_info (
    cst_id             INT,
    cst_key            VARCHAR(50),
    cst_firstname      VARCHAR(50),
    cst_lastname       VARCHAR(50),
    cst_marital_status VARCHAR(50),
    cst_gndr           VARCHAR(50),
    cst_create_date    DATE,
    dwh_create_date    DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_cst_id  (cst_id),
    INDEX idx_cst_key (cst_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS silver.crm_prd_info;

CREATE TABLE silver.crm_prd_info (
    prd_id          INT,
    cat_id          VARCHAR(50),
    prd_key         VARCHAR(50),
    prd_nm          VARCHAR(50),
    prd_cost        INT,
    prd_line        VARCHAR(50),
    prd_start_dt    DATE,
    prd_end_dt      DATE,
    dwh_create_date DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_prd_key (prd_key),
    INDEX idx_cat_id  (cat_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS silver.crm_sales_details;

CREATE TABLE silver.crm_sales_details (
    sls_ord_num     VARCHAR(50),
    sls_prd_key     VARCHAR(50),
    sls_cust_id     INT,
    sls_order_dt    DATE,
    sls_ship_dt     DATE,
    sls_due_dt      DATE,
    sls_sales       INT,
    sls_quantity    INT,
    sls_price       INT,
    dwh_create_date DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_sls_prd_key  (sls_prd_key),
    INDEX idx_sls_cust_id  (sls_cust_id),
    INDEX idx_sls_order_dt (sls_order_dt)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS silver.erp_loc_a101;

CREATE TABLE silver.erp_loc_a101 (
    cid             VARCHAR(50),
    cntry           VARCHAR(50),
    dwh_create_date DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_cid (cid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS silver.erp_cust_az12;

CREATE TABLE silver.erp_cust_az12 (
    cid             VARCHAR(50),
    bdate           DATE,
    gen             VARCHAR(50),
    dwh_create_date DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_cid (cid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS silver.erp_px_cat_g1v2;

CREATE TABLE silver.erp_px_cat_g1v2 (
    id              VARCHAR(50),
    cat             VARCHAR(50),
    subcat          VARCHAR(50),
    maintenance     VARCHAR(50),
    dwh_create_date DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_id (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;