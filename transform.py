"""
Transform: pandas equivalents of the cleansing/standardization logic that
used to live in silver.load_silver() (proc_load_silver.sql). Each function
takes a raw bronze DataFrame and returns a cleaned silver DataFrame with the
exact same business rules as the original SQL.
"""

import numpy as np
import pandas as pd


def transform_crm_cust_info(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[df["cst_id"].notna()]

    # Keep only the most recent record per customer (ROW_NUMBER() ... flag_last = 1)
    df["cst_create_date"] = pd.to_datetime(df["cst_create_date"], errors="coerce")
    df = df.sort_values("cst_create_date", ascending=False)
    df = df.drop_duplicates(subset="cst_id", keep="first")

    df["cst_firstname"] = df["cst_firstname"].astype(str).str.strip()
    df["cst_lastname"] = df["cst_lastname"].astype(str).str.strip()

    status_map = {"S": "Single", "M": "Married"}
    df["cst_marital_status"] = (
        df["cst_marital_status"].astype(str).str.strip().str.upper().map(status_map).fillna("n/a")
    )

    gndr_map = {"F": "Female", "M": "Male"}
    df["cst_gndr"] = df["cst_gndr"].astype(str).str.strip().str.upper().map(gndr_map).fillna("n/a")

    df["cst_create_date"] = df["cst_create_date"].dt.date

    return df[
        ["cst_id", "cst_key", "cst_firstname", "cst_lastname",
         "cst_marital_status", "cst_gndr", "cst_create_date"]
    ]


def transform_crm_prd_info(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["cat_id"] = df["prd_key"].str.slice(0, 5).str.replace("-", "_", regex=False)
    df["prd_key"] = df["prd_key"].str.slice(6)
    df["prd_cost"] = df["prd_cost"].fillna(0)

    line_map = {"M": "Mountain", "R": "Road", "S": "Other Sales", "T": "Touring"}
    df["prd_line"] = df["prd_line"].astype(str).str.strip().str.upper().map(line_map).fillna("n/a")

    df["prd_start_dt"] = pd.to_datetime(df["prd_start_dt"], errors="coerce")

    # End date = one day before the next start date for the same prd_key
    # (LEAD(prd_start_dt) OVER (PARTITION BY prd_key ORDER BY prd_start_dt) - 1)
    df = df.sort_values(["prd_key", "prd_start_dt"])
    next_start = df.groupby("prd_key")["prd_start_dt"].shift(-1)
    df["prd_end_dt"] = (next_start - pd.Timedelta(days=1)).dt.date
    df["prd_start_dt"] = df["prd_start_dt"].dt.date

    return df[
        ["prd_id", "cat_id", "prd_key", "prd_nm", "prd_cost",
         "prd_line", "prd_start_dt", "prd_end_dt"]
    ]


def _yyyymmdd_to_date(series: pd.Series) -> pd.Series:
    """INT YYYYMMDD -> date, with 0 / malformed values becoming NaT (NULL)."""
    as_str = series.astype("Int64").astype(str)
    as_str = as_str.where(series.notna() & (series != 0) & (as_str.str.len() == 8))
    return pd.to_datetime(as_str, format="%Y%m%d", errors="coerce")


def transform_crm_sales_details(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["sls_order_dt"] = _yyyymmdd_to_date(df["sls_order_dt"]).dt.date
    df["sls_ship_dt"] = _yyyymmdd_to_date(df["sls_ship_dt"]).dt.date
    df["sls_due_dt"] = _yyyymmdd_to_date(df["sls_due_dt"]).dt.date

    expected_sales = df["sls_quantity"] * df["sls_price"].abs()
    bad_sales = df["sls_sales"].isna() | (df["sls_sales"] <= 0) | (df["sls_sales"] != expected_sales)
    df["sls_sales"] = np.where(bad_sales, expected_sales, df["sls_sales"])

    bad_price = df["sls_price"].isna() | (df["sls_price"] <= 0)
    derived_price = df["sls_sales"] / df["sls_quantity"].replace(0, np.nan)
    df["sls_price"] = np.where(bad_price, derived_price, df["sls_price"])

    return df[
        ["sls_ord_num", "sls_prd_key", "sls_cust_id", "sls_order_dt",
         "sls_ship_dt", "sls_due_dt", "sls_sales", "sls_quantity", "sls_price"]
    ]


def transform_erp_cust_az12(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["cid"] = df["cid"].where(~df["cid"].str.startswith("NAS"), df["cid"].str.slice(3))

    df["bdate"] = pd.to_datetime(df["bdate"], errors="coerce")
    future = df["bdate"] > pd.Timestamp.now()
    df["bdate"] = df["bdate"].where(~future, pd.NaT).dt.date

    gen_clean = df["gen"].astype(str).str.strip().str.upper()
    df["gen"] = np.select(
        [gen_clean.isin(["F", "FEMALE"]), gen_clean.isin(["M", "MALE"])],
        ["Female", "Male"],
        default="n/a",
    )

    return df[["cid", "bdate", "gen"]]


def transform_erp_loc_a101(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["cid"] = df["cid"].str.replace("-", "", regex=False)

    cntry_clean = df["cntry"].astype(str).str.strip()
    df["cntry"] = np.select(
        [
            cntry_clean == "DE",
            cntry_clean.isin(["US", "USA"]),
            (cntry_clean == "") | df["cntry"].isna(),
        ],
        ["Germany", "United States", "n/a"],
        default=cntry_clean,
    )

    return df[["cid", "cntry"]]


def transform_erp_px_cat_g1v2(df: pd.DataFrame) -> pd.DataFrame:
    # Straight passthrough, matching the original SQL (no transformation).
    return df[["id", "cat", "subcat", "maintenance"]].copy()


# Maps each silver table to its transform function and its bronze source.
SILVER_TRANSFORMS = {
    "crm_cust_info": transform_crm_cust_info,
    "crm_prd_info": transform_crm_prd_info,
    "crm_sales_details": transform_crm_sales_details,
    "erp_cust_az12": transform_erp_cust_az12,
    "erp_loc_a101": transform_erp_loc_a101,
    "erp_px_cat_g1v2": transform_erp_px_cat_g1v2,
}
