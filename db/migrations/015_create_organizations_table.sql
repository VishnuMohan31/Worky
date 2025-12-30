-- Worky Database Schema - Migration 015
-- Version: 015
-- Description: Create organizations table for managing organizations with CRUD operations

-- Create organizations table
CREATE TABLE organizations (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('ORG', 'organizations_id_seq'),
    name VARCHAR(255) NOT NULL,
    logo_url VARCHAR(500),
    logo_data TEXT,
    description TEXT,
    website VARCHAR(500),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN DEFAULT true NOT NULL,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create sequence for organizations
CREATE SEQUENCE IF NOT EXISTS organizations_id_seq START 1;

-- Create indexes
CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_is_active ON organizations(is_active);
CREATE INDEX idx_organizations_is_deleted ON organizations(is_deleted);

-- Create updated_at trigger
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE organizations IS 'Organizations table for managing company/organization information with full CRUD operations';
COMMENT ON COLUMN organizations.logo_url IS 'URL to organization logo image (e.g., S3, CDN, or local path)';
COMMENT ON COLUMN organizations.logo_data IS 'Base64 encoded logo image data for embedded storage';
COMMENT ON COLUMN organizations.is_active IS 'Whether the organization is currently active';
COMMENT ON COLUMN organizations.is_deleted IS 'Soft delete flag - marks organization as deleted without removing data';

