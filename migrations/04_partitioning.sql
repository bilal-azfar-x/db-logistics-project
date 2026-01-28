BEGIN;

ALTER TABLE truck_telemetry RENAME TO truck_telemetry_old;

CREATE TABLE truck_telemetry (
    id BIGSERIAL,
    truck_license_plate TEXT,
    latitude FLOAT,
    longitude FLOAT,
    elevation INT,
    speed INT,
    engine_temp FLOAT,
    fuel_level FLOAT,
    timestamp TIMESTAMP NOT NULL
) PARTITION BY RANGE (timestamp);

-- DEFAULT partition prevents inserts from failing if timestamp is outside expected ranges
CREATE TABLE truck_telemetry_default
PARTITION OF truck_telemetry DEFAULT;

-- Create a couple of broad partitions (covers typical "this year" data)
-- You can extend later if needed.
CREATE TABLE truck_telemetry_2024
PARTITION OF truck_telemetry
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE truck_telemetry_2025
PARTITION OF truck_telemetry
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE truck_telemetry_2026
PARTITION OF truck_telemetry
FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Migrate data
INSERT INTO truck_telemetry (
    truck_license_plate, latitude, longitude, elevation, speed, engine_temp, fuel_level, timestamp
)
SELECT
    truck_license_plate, latitude, longitude, elevation, speed, engine_temp, fuel_level, timestamp
FROM truck_telemetry_old;

-- Index for the benchmark query (plate + newest first)
-- In PG15, creating index on parent propagates to partitions.
CREATE INDEX IF NOT EXISTS idx_truck_plate_ts
ON truck_telemetry (truck_license_plate, timestamp DESC);

COMMIT;
