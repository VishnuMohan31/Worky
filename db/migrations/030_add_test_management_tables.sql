-- Migration: Add Test Management Tables
-- Date: 2025-12-29
-- Description: Add tables for test runs, test cases, and bug enhancements

-- Create test_runs table
CREATE TABLE IF NOT EXISTS test_runs (
    id VARCHAR(20) PRIMARY KEY,
    project_id VARCHAR(20) REFERENCES projects(id),
    usecase_id VARCHAR(20) REFERENCES usecases(id),
    user_story_id VARCHAR(20) REFERENCES user_stories(id),
    task_id VARCHAR(20) REFERENCES tasks(id),
    subtask_id VARCHAR(20) REFERENCES subtasks(id),
    name VARCHAR(255) NOT NULL,
    purpose TEXT,
    short_description VARCHAR(500),
    long_description TEXT,
    component_attached_to VARCHAR(255),
    run_type VARCHAR(50) DEFAULT 'Misc',
    status VARCHAR(50) DEFAULT 'In Progress',
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    total_test_cases INTEGER DEFAULT 0,
    passed_test_cases INTEGER DEFAULT 0,
    failed_test_cases INTEGER DEFAULT 0,
    blocked_test_cases INTEGER DEFAULT 0,
    created_by VARCHAR(20) REFERENCES users(id) NOT NULL,
    updated_by VARCHAR(20) REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- Create test_cases table
CREATE TABLE IF NOT EXISTS test_cases (
    id VARCHAR(20) PRIMARY KEY,
    test_run_id VARCHAR(20) REFERENCES test_runs(id) NOT NULL,
    test_case_name VARCHAR(255) NOT NULL,
    test_case_description TEXT,
    test_case_steps TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    actual_result TEXT,
    inference TEXT,
    component_attached_to VARCHAR(255),
    remarks TEXT,
    priority VARCHAR(20),
    status VARCHAR(50) DEFAULT 'Not Executed',
    executed_by VARCHAR(20) REFERENCES users(id),
    executed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(20) REFERENCES users(id) NOT NULL,
    updated_by VARCHAR(20) REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- Create test_executions table
CREATE TABLE IF NOT EXISTS test_executions (
    id VARCHAR(20) PRIMARY KEY,
    test_case_id VARCHAR(20) REFERENCES test_cases(id) NOT NULL,
    test_run_id VARCHAR(20) REFERENCES test_runs(id),
    executed_by VARCHAR(20) REFERENCES users(id) NOT NULL,
    execution_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    execution_status VARCHAR(50) NOT NULL,
    actual_result TEXT,
    execution_notes TEXT,
    environment VARCHAR(100),
    browser VARCHAR(50),
    os VARCHAR(50),
    device_type VARCHAR(50),
    screenshots TEXT,
    log_files TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create test_case_bugs junction table
CREATE TABLE IF NOT EXISTS test_case_bugs (
    id VARCHAR(20) PRIMARY KEY,
    test_case_id VARCHAR(20) REFERENCES test_cases(id) NOT NULL,
    bug_id VARCHAR(20) REFERENCES bugs(id) NOT NULL,
    test_execution_id VARCHAR(20) REFERENCES test_executions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id) NOT NULL
);

-- Create test_case_comments table
CREATE TABLE IF NOT EXISTS test_case_comments (
    id VARCHAR(20) PRIMARY KEY,
    test_case_id VARCHAR(20) NOT NULL,
    comment_text TEXT NOT NULL,
    author_id VARCHAR(20) NOT NULL,
    mentioned_users TEXT,
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP WITH TIME ZONE,
    attachments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- Create bug_comments table
CREATE TABLE IF NOT EXISTS bug_comments (
    id VARCHAR(20) PRIMARY KEY,
    bug_id VARCHAR(20) NOT NULL,
    comment_text TEXT NOT NULL,
    author_id VARCHAR(20) NOT NULL,
    mentioned_users TEXT,
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP WITH TIME ZONE,
    attachments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- Create bug_attachments table
CREATE TABLE IF NOT EXISTS bug_attachments (
    id VARCHAR(20) PRIMARY KEY,
    bug_id VARCHAR(20) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_by VARCHAR(20) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- Create bug_status_history table
CREATE TABLE IF NOT EXISTS bug_status_history (
    id VARCHAR(20) PRIMARY KEY,
    bug_id VARCHAR(20) NOT NULL,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    resolution_type VARCHAR(50),
    notes TEXT,
    changed_by VARCHAR(20) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add missing columns to bugs table
DO $$
BEGIN
    -- Add test_run_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'test_run_id') THEN
        ALTER TABLE bugs ADD COLUMN test_run_id VARCHAR(20) REFERENCES test_runs(id);
    END IF;
    
    -- Add test_case_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'test_case_id') THEN
        ALTER TABLE bugs ADD COLUMN test_case_id VARCHAR(20) REFERENCES test_cases(id);
    END IF;
    
    -- Add client_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'client_id') THEN
        ALTER TABLE bugs ADD COLUMN client_id VARCHAR(20) REFERENCES clients(id);
    END IF;
    
    -- Add program_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'program_id') THEN
        ALTER TABLE bugs ADD COLUMN program_id VARCHAR(20) REFERENCES programs(id);
    END IF;
    
    -- Add project_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'project_id') THEN
        ALTER TABLE bugs ADD COLUMN project_id VARCHAR(20) REFERENCES projects(id);
    END IF;
    
    -- Add usecase_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'usecase_id') THEN
        ALTER TABLE bugs ADD COLUMN usecase_id VARCHAR(20) REFERENCES usecases(id);
    END IF;
    
    -- Add user_story_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'user_story_id') THEN
        ALTER TABLE bugs ADD COLUMN user_story_id VARCHAR(20) REFERENCES user_stories(id);
    END IF;
    
    -- Add task_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'task_id') THEN
        ALTER TABLE bugs ADD COLUMN task_id VARCHAR(20) REFERENCES tasks(id);
    END IF;
    
    -- Add subtask_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'subtask_id') THEN
        ALTER TABLE bugs ADD COLUMN subtask_id VARCHAR(20) REFERENCES subtasks(id);
    END IF;
    
    -- Add category column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'category') THEN
        ALTER TABLE bugs ADD COLUMN category VARCHAR(50);
    END IF;
    
    -- Add reporter_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'reporter_id') THEN
        ALTER TABLE bugs ADD COLUMN reporter_id VARCHAR(20) REFERENCES users(id);
    END IF;
    
    -- Add assignee_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'assignee_id') THEN
        ALTER TABLE bugs ADD COLUMN assignee_id VARCHAR(20) REFERENCES users(id);
    END IF;
    
    -- Add qa_owner_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'qa_owner_id') THEN
        ALTER TABLE bugs ADD COLUMN qa_owner_id VARCHAR(20) REFERENCES users(id);
    END IF;
    
    -- Add reproduction_steps column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'reproduction_steps') THEN
        ALTER TABLE bugs ADD COLUMN reproduction_steps TEXT;
    END IF;
    
    -- Add expected_result column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'expected_result') THEN
        ALTER TABLE bugs ADD COLUMN expected_result TEXT;
    END IF;
    
    -- Add actual_result column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'actual_result') THEN
        ALTER TABLE bugs ADD COLUMN actual_result TEXT;
    END IF;
    
    -- Add linked_task_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'linked_task_id') THEN
        ALTER TABLE bugs ADD COLUMN linked_task_id VARCHAR(20);
    END IF;
    
    -- Add linked_commit column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'linked_commit') THEN
        ALTER TABLE bugs ADD COLUMN linked_commit VARCHAR(255);
    END IF;
    
    -- Add linked_pr column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'linked_pr') THEN
        ALTER TABLE bugs ADD COLUMN linked_pr VARCHAR(255);
    END IF;
    
    -- Add component_attached_to column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'component_attached_to') THEN
        ALTER TABLE bugs ADD COLUMN component_attached_to VARCHAR(255);
    END IF;
    
    -- Add environment column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'environment') THEN
        ALTER TABLE bugs ADD COLUMN environment VARCHAR(255);
    END IF;
    
    -- Add reopen_count column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'reopen_count') THEN
        ALTER TABLE bugs ADD COLUMN reopen_count INTEGER DEFAULT 0;
    END IF;
    
    -- Add bug_type column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'bug_type') THEN
        ALTER TABLE bugs ADD COLUMN bug_type VARCHAR(50);
    END IF;
    
    -- Add resolution_type column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'resolution_type') THEN
        ALTER TABLE bugs ADD COLUMN resolution_type VARCHAR(50);
    END IF;
    
    -- Add found_in_version column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'found_in_version') THEN
        ALTER TABLE bugs ADD COLUMN found_in_version VARCHAR(50);
    END IF;
    
    -- Add fixed_in_version column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'fixed_in_version') THEN
        ALTER TABLE bugs ADD COLUMN fixed_in_version VARCHAR(50);
    END IF;
    
    -- Add browser column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'browser') THEN
        ALTER TABLE bugs ADD COLUMN browser VARCHAR(50);
    END IF;
    
    -- Add os column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'os') THEN
        ALTER TABLE bugs ADD COLUMN os VARCHAR(50);
    END IF;
    
    -- Add device_type column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'device_type') THEN
        ALTER TABLE bugs ADD COLUMN device_type VARCHAR(50);
    END IF;
    
    -- Add steps_to_reproduce column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'steps_to_reproduce') THEN
        ALTER TABLE bugs ADD COLUMN steps_to_reproduce TEXT;
    END IF;
    
    -- Add expected_behavior column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'expected_behavior') THEN
        ALTER TABLE bugs ADD COLUMN expected_behavior TEXT;
    END IF;
    
    -- Add actual_behavior column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'actual_behavior') THEN
        ALTER TABLE bugs ADD COLUMN actual_behavior TEXT;
    END IF;
    
    -- Add description column (if missing)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bugs' AND column_name = 'description') THEN
        ALTER TABLE bugs ADD COLUMN description TEXT;
    END IF;

END $$;

-- Add missing columns to entity_notes table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'entity_notes' AND column_name = 'is_decision') THEN
        ALTER TABLE entity_notes ADD COLUMN is_decision BOOLEAN DEFAULT false NOT NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'entity_notes' AND column_name = 'decision_status') THEN
        ALTER TABLE entity_notes ADD COLUMN decision_status VARCHAR(20) DEFAULT 'Active';
    END IF;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_test_runs_project ON test_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_test_runs_status ON test_runs(status);
CREATE INDEX IF NOT EXISTS idx_test_cases_run ON test_cases(test_run_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_status ON test_cases(status);
CREATE INDEX IF NOT EXISTS idx_test_executions_case ON test_executions(test_case_id);
CREATE INDEX IF NOT EXISTS idx_bug_comments_bug ON bug_comments(bug_id);
CREATE INDEX IF NOT EXISTS idx_bug_attachments_bug ON bug_attachments(bug_id);
CREATE INDEX IF NOT EXISTS idx_bug_status_history_bug ON bug_status_history(bug_id);

DO $$ BEGIN RAISE NOTICE 'Migration 030_add_test_management_tables completed successfully'; END $$;

