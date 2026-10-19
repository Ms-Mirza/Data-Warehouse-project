"""
Flask control panel for the ETL pipeline.

Runs locally alongside the existing pipeline files (it imports etl_bronze,
etl_silver, main, db, config directly — no changes needed to any of them).
Gives you:
  - Buttons to trigger the bronze load, silver load, or the full pipeline,
    with the same step-by-step log output main.py prints, captured and
    shown in the browser.
  - A simple browser for the gold layer (dim_customers, dim_products,
    fact_sales) with pagination.

Run:
    python app.py
Then open http://localhost:5000
"""

import contextlib
import io
import traceback

from flask import Flask, jsonify, render_template, request
from sqlalchemy import text

import config
import db
import etl_bronze
import etl_silver
import main as pipeline_main

app = Flask(__name__)

# Whitelist of queryable gold tables/views and the column order to display.
# Keeping this as a fixed map (rather than trusting a table name from the
# request) is what makes it safe to interpolate `table` into SQL below.
GOLD_TABLES = {
    "dim_customers": [
        "customer_key", "customer_id", "customer_number", "first_name",
        "last_name", "country", "marital_status", "gender",
        "birthdate", "create_date",
    ],
    "dim_products": [
        "product_key", "product_id", "product_number", "product_name",
        "category_id", "category", "subcategory", "maintenance",
        "cost", "product_line", "start_date",
    ],
    "fact_sales": [
        "order_number", "product_key", "customer_key", "order_date",
        "shipping_date", "due_date", "sales_amount", "quantity", "price",
    ],
}

PAGE_SIZE = 25


def _run_captured(fn) -> dict:
    """Run `fn`, capturing everything it prints, and report success/failure."""
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            fn()
        return {"success": True, "logs": buffer.getvalue()}
    except Exception:
        return {
            "success": False,
            "logs": buffer.getvalue(),
            "error": traceback.format_exc(),
        }


@app.route("/")
def index():
    return render_template("index.html", tables=list(GOLD_TABLES))


@app.route("/api/run/<stage>", methods=["POST"])
def run_stage(stage):
    stage_fns = {
        "bronze": etl_bronze.run,
        "silver": etl_silver.run,
        "all": pipeline_main.run,
    }
    fn = stage_fns.get(stage)
    if fn is None:
        return jsonify({"success": False, "error": f"Unknown stage '{stage}'"}), 400

    result = _run_captured(fn)
    return jsonify(result), (200 if result["success"] else 500)


@app.route("/api/gold/<table>")
def gold_table(table):
    if table not in GOLD_TABLES:
        return jsonify({"error": f"Unknown table '{table}'"}), 404

    page = max(int(request.args.get("page", 1)), 1)
    offset = (page - 1) * PAGE_SIZE

    try:
        engine = db.get_engine(config.GOLD_DB)
        with engine.connect() as conn:
            total = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            rows = conn.execute(
                text(f"SELECT * FROM {table} LIMIT :limit OFFSET :offset"),
                {"limit": PAGE_SIZE, "offset": offset},
            ).mappings().all()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "columns": GOLD_TABLES[table],
        "rows": [dict(r) for r in rows],
        "page": page,
        "page_size": PAGE_SIZE,
        "total": total,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
