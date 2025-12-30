-- Worky Database Schema - Migration 011
-- Version: 011
-- Description: Add company settings table for branding (logo, name, etc.)

-- Create company_settings table
-- This table stores company-wide settings including branding information
-- Only one row should exist per client (enforced by unique constraint on client_id)
CREATE TABLE company_settings (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('CMP', 'company_settings_id_seq'),
    client_id VARCHAR(20) NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    company_logo_url VARCHAR(500),
    company_logo_data TEXT,
    primary_color VARCHAR(7) DEFAULT '#4A90E2',
    secondary_color VARCHAR(7) DEFAULT '#2C3E50',
    report_header_text TEXT,
    report_footer_text TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    currency VARCHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- Create sequence for company_settings
CREATE SEQUENCE IF NOT EXISTS company_settings_id_seq START 1;

-- Create indexes
CREATE INDEX idx_company_settings_client_id ON company_settings(client_id);
CREATE INDEX idx_company_settings_is_active ON company_settings(is_active);

-- Create updated_at trigger
CREATE TRIGGER update_company_settings_updated_at BEFORE UPDATE ON company_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE company_settings IS 'Company branding and settings per client. Only one row per client. Logo can be stored as URL or base64 data.';
COMMENT ON COLUMN company_settings.company_logo_url IS 'URL to company logo image (e.g., S3, CDN, or local path)';
COMMENT ON COLUMN company_settings.company_logo_data IS 'Base64 encoded logo image data for embedded storage';
COMMENT ON COLUMN company_settings.primary_color IS 'Primary brand color in hex format (e.g., #4A90E2)';
COMMENT ON COLUMN company_settings.secondary_color IS 'Secondary brand color in hex format';
COMMENT ON COLUMN company_settings.report_header_text IS 'Custom text to display in report headers';
COMMENT ON COLUMN company_settings.report_footer_text IS 'Custom text to display in report footers (e.g., copyright, contact info)';
COMMENT ON COLUMN company_settings.timezone IS 'Default timezone for the company (e.g., America/New_York, Asia/Kolkata)';
COMMENT ON COLUMN company_settings.date_format IS 'Preferred date format (e.g., YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY)';
COMMENT ON COLUMN company_settings.currency IS 'Default currency code (ISO 4217, e.g., USD, EUR, INR)';
