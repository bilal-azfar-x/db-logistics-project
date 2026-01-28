from fastapi import FastAPI, Request
import psycopg2
import os
import time
from psycopg2.extras import RealDictCursor

app = FastAPI()
DB_URL = os.getenv("DATABASE_URL")

@app.middleware("http")
async def timing(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response

def get_conn():
    if not DB_URL:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(DB_URL)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/shipments/by-date")
def by_date(date: str):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            start = f"{date}-01 00:00:00"
            cur.execute("""
                SELECT *
                FROM shipments
                WHERE created_at >= %s::timestamp
                  AND created_at < (%s::timestamp + INTERVAL '1 month')
                LIMIT 100
            """, (start, start))
            return cur.fetchall()
    finally:
        conn.close()

@app.get("/shipments/driver/{name}")
def by_driver(name: str):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT s.*
                FROM shipments s
                JOIN drivers d ON s.driver_id = d.id
                WHERE d.name ILIKE %s
                LIMIT 50
            """, (f"{name}%",))
            return cur.fetchall()
    finally:
        conn.close()

@app.get("/finance/high-value-invoices")
def finance():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT *
                FROM finance_invoices
                WHERE (raw_invoice_data->>'amount_cents')::int > 50000
                LIMIT 100
            """)
            return cur.fetchall()
    finally:
        conn.close()

@app.get("/telemetry/truck/{plate}")
def telemetry(plate: str, limit: int = 100):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT *
                FROM truck_telemetry
                WHERE truck_license_plate = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (plate, limit))
            return cur.fetchall()
    finally:
        conn.close()

@app.get("/analytics/daily-stats")
def analytics():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT delivered, avg_speed, revenue
                FROM analytics_cache
            """)
            return cur.fetchone()
    finally:
        conn.close()
