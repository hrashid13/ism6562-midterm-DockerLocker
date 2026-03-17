"""
load_data.py
============
Loads seed SQL files into Ignite 2 via the REST API on port 8081.
Uses POST with form data to avoid URL encoding issues with SQL syntax.
"""

import os
import re
import time
import requests

IGNITE_REST = "http://ignite-node1:8081"
DATA_DIR    = "/data"
INIT_DIR    = "/init"

LOAD_ORDER = [
    (INIT_DIR, "01_schema.sql"),
    (DATA_DIR, "dim_payment_method.sql"),
    (DATA_DIR, "dim_time.sql"),
    (DATA_DIR, "dim_product.sql"),
    (DATA_DIR, "dim_customer.sql"),
    (DATA_DIR, "dim_employee.sql"),
    (DATA_DIR, "fact_sales.sql"),
]

def wait_for_cluster(retries=20, delay=5):
    print("Waiting for Ignite cluster to be ready...")
    for i in range(retries):
        try:
            r = requests.get(f"{IGNITE_REST}/ignite?cmd=version", timeout=3)
            if r.status_code == 200 and r.json().get("successStatus") == 0:
                print("Cluster is up!")
                return True
        except Exception:
            pass
        print(f"   Attempt {i+1}/{retries} -- retrying in {delay}s...")
        time.sleep(delay)
    raise RuntimeError("Could not connect to Ignite cluster after waiting.")

def create_default_cache():
    """Create a default cache to use as context for SQL execution."""
    r = requests.get(f"{IGNITE_REST}/ignite?cmd=getorcreate&cacheName=default", timeout=10)
    data = r.json()
    if data.get("successStatus") == 0:
        print("Default cache ready.")
    else:
        raise RuntimeError(f"Failed to create default cache: {data.get('error')}")

def execute_sql(stmt):
    """Execute a single SQL statement via POST to avoid URL encoding issues."""
    try:
        r = requests.post(
            f"{IGNITE_REST}/ignite",
            params={"cmd": "qryfldexe", "pageSize": "1", "cacheName": "default"},
            data={"qry": stmt},
            timeout=60
        )
        data = r.json()
        success = data.get("successStatus") == 0
        error = data.get("error", "")
        return success, error
    except Exception as e:
        return False, str(e)

def run_sql_file(filepath, label):
    print(f"\nLoading: {label}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r'--[^\n]*', '', content)
    statements = [s.strip() for s in content.split(";") if s.strip()]
    total = len(statements)
    print(f"   {total} statements found")

    success = 0
    for i, stmt in enumerate(statements):
        ok, error = execute_sql(stmt)
        if ok:
            success += 1
        else:
            print(f"   Statement {i+1} failed: {error[:120]}")

        if (i + 1) % 1000 == 0:
            print(f"   ... {i+1}/{total} done")

    print(f"   {success}/{total} loaded successfully")

def main():
    wait_for_cluster()
    create_default_cache()

    for folder, filename in LOAD_ORDER:
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            run_sql_file(filepath, filename)
        else:
            print(f"\nSkipping {filename} -- file not found")

    print("\nAll data loaded. Cluster is ready for demo queries.")

if __name__ == "__main__":
    main()
