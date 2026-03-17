"""
prepare_data.py
===============
Run this ONCE on your laptop before committing to GitHub.
Transforms the DBeaver SQL exports into Ignite-compatible inserts.

Usage:
    python scripts/prepare_data.py

Input:  raw SQL files in ./raw/         (your DBeaver exports)
Output: cleaned SQL files in ./data/    (Ignite-ready, goes in repo)
"""

import os
import re

RAW_DIR    = "./raw"
OUTPUT_DIR = "./data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Column renames needed for Ignite compatibility.
# 'name', 'cost', and 'method' are reserved words in some SQL contexts.
COLUMN_RENAMES = {
    "dim_product":        {'"name"': "product_name"},
    "dim_customer":       {'"name"': "customer_name"},
    "dim_employee":       {'"name"': "employee_name", '"role"': "emp_role"},
    "fact_sales":         {'"cost"': "cost"},
    "dim_payment_method": {'"method"': "method"},
}

# Each table's column list as exported by DBeaver (without id).
# We use this to inject id into both the column list and values.
TABLE_COLUMNS = {
    "dim_time":           "simulated_day,hour_of_day,time_label,part_of_day,is_rush_hour",
    "dim_product":        "source_id,product_name,category,subcategory,unit_cost",
    "dim_customer":       "source_id,customer_name,is_loyalty,join_date",
    "dim_employee":       "source_id,employee_name,role",
    "dim_payment_method": "method",
    "fact_sales":         "dim_time_id,dim_product_id,dim_customer_id,dim_employee_id,dim_payment_method_id,source_transaction_id,simulated_day,quantity_sold,unit_price,unit_cost,revenue,cost,profit",
}

def clean_sql(content, table_name):
    """Clean a DBeaver SQL export for Ignite compatibility."""

    # Remove schema prefix (public.tablename -> tablename)
    content = re.sub(r'\bpublic\.', '', content)

    # Apply column renames
    if table_name in COLUMN_RENAMES:
        for old, new in COLUMN_RENAMES[table_name].items():
            content = content.replace(old, new)

    # Remove ON CONFLICT clauses (not supported in Ignite 3)
    content = re.sub(r'\s*ON CONFLICT[^;]*', '', content, flags=re.IGNORECASE)

    # Convert tab indents to spaces
    content = re.sub(r'\t+', ' ', content)

    # Strip trailing whitespace
    lines = [line.rstrip() for line in content.splitlines()]
    content = '\n'.join(lines)

    return content

def add_ids(content, table_name):
    """
    DBeaver skips the SERIAL id column for all tables.
    This injects sequential IDs into both the column list and value rows.
    """
    print(f"  Adding IDs to {table_name} rows...")

    cols = TABLE_COLUMNS.get(table_name, "")

    # Fix column list on every INSERT line using regex
    content = re.sub(
        rf'INSERT INTO {table_name} \((?!id,)',
        f'INSERT INTO {table_name} (id,',
        content
    )

    # Fix value rows -- inject sequential id as first value
    row_id = 1
    output_lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith('(') and not stripped.upper().startswith('INSERT'):
            stripped = f'({row_id},' + stripped[1:]
            row_id += 1
            output_lines.append(' ' + stripped)
        else:
            output_lines.append(line)

    print(f"  Added IDs for {row_id - 1} rows")
    return '\n'.join(output_lines)

def process_file(filename):
    raw_path    = os.path.join(RAW_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(raw_path):
        print(f"Not found: {raw_path} -- skipping")
        return

    print(f"\nProcessing: {filename}")

    with open(raw_path, 'r', encoding='utf-8') as f:
        content = f.read()

    table_name = filename.replace('.sql', '')
    content = clean_sql(content, table_name)
    content = add_ids(content, table_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Saved to {output_path} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    print("=" * 50)
    print("Grocery Store Data Prep -- Ignite Compatibility")
    print("=" * 50)

    files = [
        "dim_payment_method.sql",
        "dim_time.sql",
        "dim_product.sql",
        "dim_customer.sql",
        "dim_employee.sql",
        "fact_sales.sql",
    ]

    for f in files:
        process_file(f)

    print("\nAll files processed. Check ./data/ and commit to GitHub.")
