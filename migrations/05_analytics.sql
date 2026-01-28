BEGIN;

DROP MATERIALIZED VIEW IF EXISTS analytics_cache;

CREATE MATERIALIZED VIEW analytics_cache AS
SELECT
    1 AS id,
    (SELECT COUNT(*) FROM shipments WHERE status='DELIVERED') AS delivered,
    (SELECT AVG(speed) FROM truck_telemetry) AS avg_speed,
    (SELECT SUM((raw_invoice_data->>'amount_cents')::int) FROM finance_invoices) AS revenue;

CREATE UNIQUE INDEX IF NOT EXISTS idx_analytics_cache_id
ON analytics_cache (id);

COMMIT;
