BEGIN;

ALTER TABLE shipments
ALTER COLUMN created_at TYPE TIMESTAMP
USING created_at::timestamp;

CREATE INDEX IF NOT EXISTS idx_shipments_created_at
ON shipments (created_at);

-- helps if you ever filter by status too
CREATE INDEX IF NOT EXISTS idx_shipments_status
ON shipments (status);

COMMIT;
