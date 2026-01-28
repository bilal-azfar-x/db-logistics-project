# Legacy Logistics Rescue Mission – Technical Report

---

## 1. Executive Summary

The Legacy Logistics system initially suffered from severe performance issues due to an unoptimized PostgreSQL schema and inefficient query patterns. API response times ranged from 5–30 seconds, and the benchmark score was effectively 0%, with frequent request timeouts.

After systematically applying indexing, normalization, JSON optimization, partitioning, and caching techniques—without upgrading hardware—the system achieved a final benchmark score of 92.34%, with all API endpoints responding well under the required latency thresholds.

Final Verdict:  
High Performance. Ready for Production.

---

## 2. Problem Analysis (Before Optimization)

This section outlines the main performance bottlenecks identified during analysis, following the weekly structure of the course.

### Week 1–2: Unindexed Date Search

Problem:  
The shipments.created_at column was stored as TEXT, and date filtering was performed using the LIKE operator. This forced PostgreSQL to perform a full table scan on approximately 500,000 rows.

Before EXPLAIN (simplified):

    Seq Scan on shipments
      Filter: (created_at LIKE '2023-05%')

Impact:  
High CPU usage and slow response times for date-based shipment queries.

---

### Week 3: Unnormalized Driver Data

Problem:  
Driver information was stored as a comma-separated string inside the shipments table. Searching by driver name required substring matching, which could not utilize indexes.

Before EXPLAIN (simplified):

    Seq Scan on shipments
      Filter: (driver_details LIKE '%John%')

Impact:  
Inefficient string parsing and poor query performance.

---

### Week 4: JSON Stored as TEXT

Problem:  
Invoice data was stored as raw TEXT, requiring JSON parsing and casting during query execution.

Before EXPLAIN (simplified):

    Seq Scan on finance_invoices
      Filter: ((raw_invoice_data::json->>'amount_cents')::int > 50000)

Impact:  
CPU-intensive queries and slow finance endpoint responses.

---

### Week 5: Large Telemetry Table

Problem:  
The truck_telemetry table contained over 2 million rows with no partitioning, causing full-table scans even for limited queries.

Before EXPLAIN (simplified):

    Seq Scan on truck_telemetry

Impact:  
High I/O cost and degraded performance.

---

### Week 7: Real-Time Analytics Aggregation

Problem:  
Analytics data was calculated in real time using multiple aggregate subqueries across large tables.

Before EXPLAIN (simplified):

    Aggregate
      -> Seq Scan on shipments
      -> Seq Scan on truck_telemetry
      -> Seq Scan on finance_invoices

Impact:  
Multi-second response times for analytics endpoints.

---

## 3. The Solution (After Optimization)

Each identified issue was resolved using appropriate database optimization techniques.

### Week 1–2 Solution: Proper Data Types and Indexing

Actions Taken:
- Converted created_at from TEXT to TIMESTAMP
- Added a B-tree index on the created_at column

After EXPLAIN (simplified):

    Index Scan using idx_shipments_created_at on shipments

Result:  
Date-based searches now execute in milliseconds.

---

### Week 3 Solution: Normalization

Actions Taken:
- Created a separate drivers table
- Replaced string parsing with foreign key joins
- Indexed drivers.name and shipments.driver_id

After EXPLAIN (simplified):

    Nested Loop
      -> Index Scan on drivers (idx_drivers_name)
      -> Index Scan on shipments (idx_shipments_driver_id)

Result:  
Efficient joins with predictable performance.

---

### Week 4 Solution: JSONB Optimization

Actions Taken:
- Converted invoice data from TEXT to JSONB
- Added an expression index on amount_cents

After EXPLAIN (simplified):

    Bitmap Index Scan on idx_finance_amount_cents

Result:  
Fast JSON filtering without runtime parsing overhead.

---

### Week 5 Solution: Declarative Partitioning

Actions Taken:
- Rebuilt truck_telemetry as a range-partitioned table by timestamp
- Added indexes on (truck_license_plate, timestamp DESC)
- Added a DEFAULT partition to prevent insert failures

After EXPLAIN (simplified):

    Append
      -> Index Scan on relevant partition only

Result:  
Partition pruning ensures only relevant data is scanned.

---

### Week 7 Solution: Materialized View for Analytics

Actions Taken:
- Created a materialized view (analytics_cache) with precomputed metrics
- Added a unique index for fast access
- Replaced real-time aggregation with a simple SELECT

After EXPLAIN (simplified):

    Index Scan on analytics_cache

Result:  
Analytics endpoint responds in under 15 milliseconds.

---

## 4. Challenges Faced and Resolutions

Docker Volume Persistence:  
The database appeared populated even after deleting containers. This was caused by Docker volumes persisting across restarts. The issue was resolved using docker-compose down -v to fully reset the database state.

PostgreSQL Constraint Syntax Error:  
PostgreSQL does not support ADD CONSTRAINT IF NOT EXISTS. The migration was corrected by removing the clause and ensuring proper migration order.

API Crashing After Changes:  
The API container was reseeding the database on every restart because seed.py was executed in the Dockerfile CMD. This caused database corruption and benchmark failures.

Resolution:  
Initialization was separated from runtime. The seeder is now run manually once, and the API starts without reseeding.

Benchmark Showing ERROR for All Endpoints:  
Repeated container restarts caused connection resets and benchmark timeouts.

Resolution:  
Stabilizing the container lifecycle and removing automatic reseeding restored consistent API availability.

---

## Final Outcome

Initial Benchmark Score: ~0%  
Final Benchmark Score: 92.34%  

System State: Stable, optimized, and production-ready.  
All constraints were respected, including no hardware upgrades and live migrations only.