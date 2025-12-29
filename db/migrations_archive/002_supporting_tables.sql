-- Worky Database Schema - Supporting Tables
-- Version: 002
-- Description: Dependencies, commits, bugs, documentation, and audit logs

-- Dependencies table (supports all hierarchy levels)
CREATE TABLE dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Program', 'Project', 'Usecase', 'UserStory', 'Task', 'Subtask')),
    entity_id UUID NOT NULL,
    depends_on_type VARCHAR(50) NOT NULL CHECK (depends_on_type IN ('Program', 'Project', 'Usecase', 'UserStory', 'Task', 'Subtask')),
    depends_on_id UUID NOT NULL,
    dependency_type VARCHAR(50) DEFAULT 'finish_to_start' CHECK (dependency_type IN ('finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Commits table (Git integration)
CREATE TABLE commits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    repository VARCHAR(255) NOT NULL,
    commit_hash VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    author_email VARCHAR(255),
    message TEXT NOT NULL,
    committed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    branch VARCHAR(255),
    url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pull Requests table
CREATE TABLE pull_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    repository VARCHAR(255) NOT NULL,
    pr_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    author VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    merged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bugs table
CREATE TABLE bugs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_story_id UUID REFERENCES user_stories(id) ON DELETE SET NULL,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('Urgent', 'High', 'Medium', 'Low')),
    status VARCHAR(50) DEFAULT 'New' CHECK (status IN ('New', 'Assigned', 'In Progress', 'Fixed', 'Verified', 'Closed', 'Reopened')),
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    reported_by UUID NOT NULL REFERENCES users(id),
    environment VARCHAR(100),
    steps_to_reproduce TEXT,
    expected_behavior TEXT,
    actual_behavior TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE
);

-- Documentation table
CREATE TABLE documentation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Client', 'Program', 'Project', 'Usecase', 'UserStory', 'Task')),
    entity_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    format VARCHAR(20) DEFAULT 'markdown' CHECK (format IN ('markdown', 'html', 'plain')),
    version INTEGER DEFAULT 1,
    author_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    changes JSONB,
    request_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Report Snapshots table
CREATE TABLE report_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    parameters JSONB,
    data JSONB NOT NULL,
    generated_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sprints table
CREATE TABLE sprints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    goal TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Planning' CHECK (status IN ('Planning', 'Active', 'Completed', 'Cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sprint Tasks (many-to-many relationship)
CREATE TABLE sprint_tasks (
    sprint_id UUID NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (sprint_id, task_id)
);

-- Create indexes
CREATE INDEX idx_dependencies_entity ON dependencies(entity_type, entity_id);
CREATE INDEX idx_dependencies_depends_on ON dependencies(depends_on_type, depends_on_id);

CREATE INDEX idx_commits_task_id ON commits(task_id);
CREATE INDEX idx_commits_hash ON commits(commit_hash);
CREATE INDEX idx_commits_repository ON commits(repository);

CREATE INDEX idx_pull_requests_task_id ON pull_requests(task_id);
CREATE INDEX idx_pull_requests_status ON pull_requests(status);

CREATE INDEX idx_bugs_status ON bugs(status);
CREATE INDEX idx_bugs_severity ON bugs(severity);
CREATE INDEX idx_bugs_assigned_to ON bugs(assigned_to);
CREATE INDEX idx_bugs_reported_by ON bugs(reported_by);
CREATE INDEX idx_bugs_user_story_id ON bugs(user_story_id);
CREATE INDEX idx_bugs_task_id ON bugs(task_id);

CREATE INDEX idx_documentation_entity ON documentation(entity_type, entity_id);
CREATE INDEX idx_documentation_author_id ON documentation(author_id);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

CREATE INDEX idx_report_snapshots_type ON report_snapshots(report_type);
CREATE INDEX idx_report_snapshots_generated_by ON report_snapshots(generated_by);

CREATE INDEX idx_sprints_project_id ON sprints(project_id);
CREATE INDEX idx_sprints_status ON sprints(status);
CREATE INDEX idx_sprints_dates ON sprints(start_date, end_date);

CREATE INDEX idx_sprint_tasks_sprint_id ON sprint_tasks(sprint_id);
CREATE INDEX idx_sprint_tasks_task_id ON sprint_tasks(task_id);

-- Apply updated_at triggers
CREATE TRIGGER update_bugs_updated_at BEFORE UPDATE ON bugs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documentation_updated_at BEFORE UPDATE ON documentation
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pull_requests_updated_at BEFORE UPDATE ON pull_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sprints_updated_at BEFORE UPDATE ON sprints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
