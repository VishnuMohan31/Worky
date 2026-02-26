-- Fix initialization issues
-- This script ensures the database is properly initialized

-- 1. Create information_schema.types view if it doesn't exist
CREATE OR REPLACE VIEW information_schema.types AS
SELECT 
    n.nspname AS user_defined_type_schema,
    t.typname AS user_defined_type_name,
    'DISTINCT' AS user_defined_type_category
FROM pg_type t
JOIN pg_namespace n ON t.typnamespace = n.oid
WHERE t.typtype = 'd';

-- 2. Fix all sequences to start from the correct value
DO $$
DECLARE
    seq_name TEXT;
    table_name TEXT;
    max_id INTEGER;
BEGIN
    -- Fix users sequence
    IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'users_id_seq') THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM 5) AS INTEGER)), 0) INTO max_id FROM users;
        EXECUTE format('SELECT setval(''users_id_seq'', %s)', max_id);
        RAISE NOTICE 'Fixed users_id_seq to %', max_id;
    END IF;
    
    -- Fix clients sequence
    IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'clients_id_seq') THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM 5) AS INTEGER)), 0) INTO max_id FROM clients;
        EXECUTE format('SELECT setval(''clients_id_seq'', %s)', max_id);
        RAISE NOTICE 'Fixed clients_id_seq to %', max_id;
    END IF;
    
    -- Add more sequences as needed
END $$;
