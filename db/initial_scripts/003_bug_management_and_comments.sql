-- ============================================================================
-- Worky Database - Bug Management and Comments Schema
-- ============================================================================
-- This file contains tables for enhanced bug management:
-- - Bug comments and attachments
-- - Bug status history
-- - Test case comments
-- - Additional supporting tables
-- ============================================================================

-- ============================================================================
-- SECTION 1: BUG MANAGEMENT ENHANCEMENT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Bug Comments Table
-- ----------------------------------------------------------------------------
CREATE TABLE bug_comments (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('BC', 'bug_comments_id_seq'),
    bug_id VARCHAR(20) NOT NULL REFERENCES bugs(id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL,
    author_id VARCHAR(20) NOT NULL REFERENCES users(id),
    mentioned_users TEXT,
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP WITH TIME ZONE,
    attachments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- ----------------------------------------------------------------------------
-- Bug Attachments Table
-- ----------------------------------------------------------------------------
CREATE TABLE bug_attachments (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('BA', 'bug_attachments_id_seq'),
    bug_id VARCHAR(20) NOT NULL REFERENCES bugs(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_by VARCHAR(20) NOT NULL REFERENCES users(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- ----------------------------------------------------------------------------
-- Bug Status History Table
-- ----------------------------------------------------------------------------
CREATE TABLE bug_status_history (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('BSH', 'bug_status_history_id_seq'),
    bug_id VARCHAR(20) NOT NULL REFERENCES bugs(id) ON DELETE CASCADE,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    resolution_type VARCHAR(50),
    notes TEXT,
    changed_by VARCHAR(20) NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SECTION 2: TEST CASE COMMENTS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Test Case Comments Table
-- ----------------------------------------------------------------------------
CREATE TABLE test_case_comments (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TCC', 'test_case_comments_id_seq'),
    test_case_id VARCHAR(20) NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL,
    author_id VARCHAR(20) NOT NULL REFERENCES users(id),
    mentioned_users TEXT,
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP WITH TIME ZONE,
    attachments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- ============================================================================
-- SECTION 3: SEQUENCES FOR NEW TABLES
-- ============================================================================

-- Add sequences for the new comment and attachment tables
CREATE SEQUENCE IF NOT EXISTS bug_comments_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS bug_attachments_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS bug_status_history_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS test_case_comments_id_seq START 1;

-- ============================================================================
-- SECTION 4: INDEXES FOR PERFORMANCE
-- ============================================================================

-- Bug management indexes
CREATE INDEX idx_bug_comments_bug_id ON bug_comments(bug_id);
CREATE INDEX idx_bug_comments_author_id ON bug_comments(author_id);
CREATE INDEX idx_bug_comments_created_at ON bug_comments(created_at);
CREATE INDEX idx_bug_comments_is_deleted ON bug_comments(is_deleted);

CREATE INDEX idx_bug_attachments_bug_id ON bug_attachments(bug_id);
CREATE INDEX idx_bug_attachments_uploaded_by ON bug_attachments(uploaded_by);
CREATE INDEX idx_bug_attachments_uploaded_at ON bug_attachments(uploaded_at);
CREATE INDEX idx_bug_attachments_is_deleted ON bug_attachments(is_deleted);

CREATE INDEX idx_bug_status_history_bug_id ON bug_status_history(bug_id);
CREATE INDEX idx_bug_status_history_changed_by ON bug_status_history(changed_by);
CREATE INDEX idx_bug_status_history_changed_at ON bug_status_history(changed_at);
CREATE INDEX idx_bug_status_history_to_status ON bug_status_history(to_status);

-- Test case comments indexes
CREATE INDEX idx_test_case_comments_test_case_id ON test_case_comments(test_case_id);
CREATE INDEX idx_test_case_comments_author_id ON test_case_comments(author_id);
CREATE INDEX idx_test_case_comments_created_at ON test_case_comments(created_at);
CREATE INDEX idx_test_case_comments_is_deleted ON test_case_comments(is_deleted);

-- ============================================================================
-- SECTION 5: TRIGGERS
-- ============================================================================

-- Updated_at triggers for comment tables
CREATE TRIGGER update_bug_comments_updated_at BEFORE UPDATE ON bug_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_case_comments_updated_at BEFORE UPDATE ON test_case_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SECTION 6: FUNCTIONS FOR BUG STATUS TRACKING
-- ============================================================================

-- Function to automatically log bug status changes
CREATE OR REPLACE FUNCTION log_bug_status_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Only log if status actually changed
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO bug_status_history (
            bug_id,
            from_status,
            to_status,
            changed_by,
            changed_at
        ) VALUES (
            NEW.id,
            OLD.status,
            NEW.status,
            NEW.updated_by,
            NOW()
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically log bug status changes
CREATE TRIGGER trigger_log_bug_status_change
    AFTER UPDATE ON bugs
    FOR EACH ROW
    EXECUTE FUNCTION log_bug_status_change();

-- ============================================================================
-- SECTION 7: VIEWS FOR BUG MANAGEMENT
-- ============================================================================

-- Bug Details View with Latest Status Change
CREATE OR REPLACE VIEW bug_details_with_history AS
SELECT 
    b.*,
    bsh.from_status as previous_status,
    bsh.changed_at as status_changed_at,
    bsh.changed_by as status_changed_by,
    u_changed.full_name as status_changed_by_name,
    u_assigned.full_name as assigned_to_name,
    u_reported.full_name as reported_by_name,
    (SELECT COUNT(*) FROM bug_comments bc WHERE bc.bug_id = b.id AND bc.is_deleted = false) as comment_count,
    (SELECT COUNT(*) FROM bug_attachments ba WHERE ba.bug_id = b.id AND ba.is_deleted = false) as attachment_count
FROM bugs b
LEFT JOIN LATERAL (
    SELECT from_status, changed_at, changed_by
    FROM bug_status_history 
    WHERE bug_id = b.id 
    ORDER BY changed_at DESC 
    LIMIT 1
) bsh ON true
LEFT JOIN users u_changed ON bsh.changed_by = u_changed.id
LEFT JOIN users u_assigned ON b.assigned_to = u_assigned.id
LEFT JOIN users u_reported ON b.reported_by = u_reported.id
WHERE b.is_deleted = false;

-- Recent Bug Comments View
CREATE OR REPLACE VIEW recent_bug_comments AS
SELECT 
    bc.*,
    u.full_name as author_name,
    u.email as author_email,
    b.title as bug_title,
    b.status as bug_status
FROM bug_comments bc
JOIN users u ON bc.author_id = u.id
JOIN bugs b ON bc.bug_id = b.id
WHERE bc.is_deleted = false
ORDER BY bc.created_at DESC;

-- ============================================================================
-- SECTION 8: COMMENTS AND DOCUMENTATION
-- ============================================================================

-- Table comments
COMMENT ON TABLE bug_comments IS 'Comments on bugs for collaboration and discussion';
COMMENT ON TABLE bug_attachments IS 'File attachments for bugs (screenshots, logs, etc.)';
COMMENT ON TABLE bug_status_history IS 'History of bug status changes for audit trail';
COMMENT ON TABLE test_case_comments IS 'Comments on test cases for collaboration';

-- Column comments
COMMENT ON COLUMN bug_comments.mentioned_users IS 'JSON array of user IDs mentioned in the comment';
COMMENT ON COLUMN bug_comments.attachments IS 'JSON array of attachment references';
COMMENT ON COLUMN bug_attachments.file_size IS 'File size in bytes';
COMMENT ON COLUMN bug_status_history.resolution_type IS 'Type of resolution: Fixed, Duplicate, Won''t Fix, etc.';

-- View comments
COMMENT ON VIEW bug_details_with_history IS 'Comprehensive bug view with status history and counts';
COMMENT ON VIEW recent_bug_comments IS 'Recent bug comments with author and bug details';

-- ============================================================================
-- END OF BUG MANAGEMENT AND COMMENTS SCHEMA
-- ============================================================================