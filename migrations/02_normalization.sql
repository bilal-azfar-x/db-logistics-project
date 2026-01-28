BEGIN;

-- 1. Create drivers table
CREATE TABLE IF NOT EXISTS drivers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    license_plate TEXT
);

-- 2. Populate drivers table from shipments (deduplicate)
INSERT INTO drivers (name, phone, license_plate)
SELECT DISTINCT
    split_part(driver_details, ',', 1), -- Name
    split_part(driver_details, ',', 2), -- Phone
    split_part(driver_details, ',', 3)  -- License Plate
FROM shipments
WHERE driver_details IS NOT NULL;

-- 3. Index driver name for fast lookup
CREATE INDEX IF NOT EXISTS idx_drivers_name
ON drivers(name);

-- 4. Add driver_id column to shipments
ALTER TABLE shipments
ADD COLUMN IF NOT EXISTS driver_id INT;

-- 5. Backfill driver_id using normalized data
UPDATE shipments s
SET driver_id = d.id
FROM drivers d
WHERE split_part(s.driver_details, ',', 1) = d.name
  AND split_part(s.driver_details, ',', 3) = d.license_plate;

-- 6. Index driver_id for join performance
CREATE INDEX IF NOT EXISTS idx_shipments_driver_id
ON shipments(driver_id);

COMMIT;