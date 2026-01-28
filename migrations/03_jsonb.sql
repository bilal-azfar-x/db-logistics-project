BEGIN;

ALTER TABLE finance_invoices
ALTER COLUMN raw_invoice_data TYPE JSONB
USING raw_invoice_data::jsonb;

-- Expression index for amount_cents comparisons
CREATE INDEX IF NOT EXISTS idx_finance_amount_cents
ON finance_invoices (((raw_invoice_data->>'amount_cents')::int));

COMMIT;
