-- Worky Database Schema - Migration 025
-- Version: 025
-- Description: Add contact information (email and phone) to clients table

-- Add email and phone columns to clients table
ALTER TABLE clients 
ADD COLUMN email VARCHAR(255),
ADD COLUMN phone VARCHAR(50);

-- Add indexes for better query performance
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_clients_phone ON clients(phone);

-- Add comments for documentation
COMMENT ON COLUMN clients.email IS 'Primary contact email for the client organization';
COMMENT ON COLUMN clients.phone IS 'Primary contact phone number for the client organization';

-- Update existing clients with sample contact information (optional - for development)
-- This can be removed in production
UPDATE clients SET 
    email = CASE 
        WHEN name = 'DataLegos' THEN 'contact@datalegos.com'
        WHEN name = 'Acme Corp' THEN 'info@acmecorp.com'
        WHEN name = 'TechStart Inc' THEN 'hello@techstart.com'
        WHEN name = 'Vishnu' THEN 'contact@vishnu.com'
        ELSE LOWER(REPLACE(name, ' ', '')) || '@example.com'
    END,
    phone = CASE 
        WHEN name = 'DataLegos' THEN '+1-555-0123'
        WHEN name = 'Acme Corp' THEN '+1-555-0456'
        WHEN name = 'TechStart Inc' THEN '+1-555-0789'
        WHEN name = 'Vishnu' THEN '+1-555-0321'
        ELSE '+1-555-' || LPAD((RANDOM() * 9999)::INTEGER::TEXT, 4, '0')
    END
WHERE email IS NULL OR phone IS NULL;