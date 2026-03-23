-- Fix initialization: runs before all other migrations
-- Only performs safe operations that don't depend on tables existing yet

-- Ensure information_schema.types view exists (used by some trigger guards)
CREATE OR REPLACE VIEW information_schema.types AS
SELECT 
    n.nspname AS user_defined_type_schema,
    t.typname AS user_defined_type_name,
    'DISTINCT' AS user_defined_type_category
FROM pg_type t
JOIN pg_namespace n ON t.typnamespace = n.oid
WHERE t.typtype = 'd';
