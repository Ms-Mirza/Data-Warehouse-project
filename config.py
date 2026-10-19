"""
Central configuration for the ETL pipeline.

Reads DB credentials from environment variables (via a .env file, see
.env.example) rather than hardcoding them, and defines where each source
CSV lives plus the column names/order each bronze table expects.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- MySQL connection -------------------------------------------------------
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = os.getenv("MYSQL_PORT", "3306")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

BRONZE_DB = "bronze"
SILVER_DB = "silver"
GOLD_DB = "gold"

# --- Source files ------------------------------------------------------------
# Point DATA_DIR at wherever you keep the course's source_crm/ and source_erp/
# folders (set DATA_DIR in .env, or drop them next to this file as ./datasets).
DATA_DIR = Path(os.getenv("DATA_DIR", "./datasets"))

SOURCE_FILES = {
    "crm_cust_info":     DATA_DIR / "source_crm" / "cust_info.csv",
    "crm_prd_info":      DATA_DIR / "source_crm" / "prd_info.csv",
    "crm_sales_details": DATA_DIR / "source_crm" / "sales_details.csv",
    "erp_loc_a101":      DATA_DIR / "source_erp" / "loc_a101.csv",
    "erp_cust_az12":     DATA_DIR / "source_erp" / "cust_az12.csv",
    "erp_px_cat_g1v2":   DATA_DIR / "source_erp" / "px_cat_g1v2.csv",
}

# Column order/names for each bronze table, matching 02_ddl_bronze.sql.
# The CSV's own header row is skipped (header=0) and replaced with these,
# so this list also defines the column ORDER the CSV must be in.
BRONZE_COLUMNS = {
    "crm_cust_info": [
        "cst_id", "cst_key", "cst_firstname", "cst_lastname",
        "cst_marital_status", "cst_gndr", "cst_create_date",
    ],

    "crm_prd_info": [
        "prd_id", "prd_key", "prd_nm", "prd_cost",
        "prd_line", "prd_start_dt", "prd_end_dt",
    ],

    "crm_sales_details": [
        "sls_ord_num", "sls_prd_key", "sls_cust_id",
        "sls_order_dt", "sls_ship_dt", "sls_due_dt",
        "sls_sales", "sls_quantity", "sls_price",
    ],

    "erp_loc_a101": ["cid", "cntry"],

    "erp_cust_az12": ["cid", "bdate", "gen"],
    
    "erp_px_cat_g1v2": ["id", "cat", "subcat", "maintenance"],
}
