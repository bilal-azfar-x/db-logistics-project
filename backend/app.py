# backend/app.py
from fastapi import FastAPI, Request
import time
import psycopg2
import os
import json

app = FastAPI()
DB_URL = os.getenv("DATABASE_URL")

# --- PERFORMANCE LOGGER MIDDLEWARE ---
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.get("/")
def read_root():
    return {"message": "System Online. Performance: CRITICAL."}

# --- WEEK 1-2: Indexing Targets ---
@app.get("/shipments/by-date")
def get_by_date(date: str):
    conn = get_db_connection()
    cur = conn.cursor()
    # BAD: LIKE query on text date
    cur.execute(f"SELECT * FROM shipments WHERE created_at LIKE '{date}%'")
    rows = cur.fetchall()
    conn.close()
    return rows

# --- WEEK 3: Normalization Target ---
@app.get("/shipments/driver/{name}")
def get_by_driver(name: str):
    conn = get_db_connection()
    cur = conn.cursor()
    # BAD: Partial string match on un-normalized column
    cur.execute("SELECT * FROM shipments WHERE driver_details LIKE %s", (f"%{name}%",))
    rows = cur.fetchall()
    conn.close()
    return rows

# --- WEEK 4: JSON Target ---
@app.get("/finance/high-value-invoices")
def get_high_value():
    conn = get_db_connection()
    cur = conn.cursor()
    # BAD: Parsing JSON text at runtime
    cur.execute("SELECT * FROM finance_invoices WHERE CAST(raw_invoice_data::json->>'amount_cents' AS INT) > 50000")
    rows = cur.fetchall()
    conn.close()
    return rows

# --- WEEK 5: Partitioning Target ---
@app.get("/telemetry/truck/{plate}")
def get_truck_history(plate: str):
    conn = get_db_connection()
    cur = conn.cursor()
    # BAD: Scanning 1M rows
    cur.execute("SELECT * FROM truck_telemetry WHERE truck_license_plate = %s ORDER BY timestamp DESC LIMIT 100", (plate,))
    rows = cur.fetchall()
    conn.close()
    return rows

# --- WEEK 7: Analytics Target ---
@app.get("/analytics/daily-stats")
def get_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    # BAD: Real-time aggregation
    sql = """
    SELECT 
        (SELECT COUNT(*) FROM shipments WHERE status='DELIVERED') as delivered,
        (SELECT AVG(speed) FROM truck_telemetry) as avg_speed,
        (SELECT SUM(CAST(raw_invoice_data::json->>'amount_cents' AS INT)) FROM finance_invoices) as revenue
    """
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows