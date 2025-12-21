# Team Assignment System Deployment Guide

## Pre-Deployment Checklist

### Database Preparation

- [ ] Backup existing database
- [ ] Run migration 027_create_notification_system.sql
- [ ] Verify all indexes are created
- [ ] Test migration rollback procedures
- [ ] Validate data integrity after migration

### Environment Configuration

- [ ] Update environment variables for caching
- [ ] Configure notification service settings
- [ ] Set up performance monitoring
- [ ] Configure logging levels
- [ ] Test database connection pooling

### Code Deployment

- [ ] Deploy API changes to staging
- [ ] Deploy UI components to staging
- [ ] Run integration tests in staging
- [ ] Verify all endpoints are accessible
- [ ] Test notification delivery

## Deployment Scripts

### Database Migration Script

```bash
#!/bin/bash
# deploy_team_assignment_db.sh

set -e

echo "Starting Team Assignment System database deployment..."

# Backup database
echo "Creating database backup..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migration
echo "Running database migration..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f db/migrations/027_create_notification_system.sql

# Verify migration
echo "Verifying migration..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('notifications', 'notification_preferences', 'notification_history');"

echo "Database migration completed successfully!"
```

### API Deployment Script

```bash
#!/bin/bash
# deploy_team_assignment_api.sh

set -e

echo "Deploying Team Assignment System API..."

# Build and deploy API
docker build -t worky-api:team-assignment ./api
docker tag worky-api:team-assignment worky-api:latest

# Update running containers
docker-compose down api
docker-compose up -d api

# Wait for API to be ready
echo "Waiting for API to be ready..."
sleep 30

# Health check
curl -f http://localhost:8007/api/v1/performance/system/health || exit 1

echo "API deployment completed successfully!"
```

### UI Deployment Script

```bash
#!/bin/bash
# deploy_team_assignment_ui.sh

set -e

echo "Deploying Team Assignment System UI..."

# Build UI
cd ui
npm run build

# Deploy to web server
rsync -av dist/ /var/www/worky/

# Restart web server
systemctl reload nginx

echo "UI deployment completed successfully!"
```

## Feature Flags Configuration

```python
# Feature flags for gradual rollout
FEATURE_FLAGS = {
    "team_assignment_system": {
        "enabled": True,
        "rollout_percentage": 100,  # Start with 10%, increase gradually
        "allowed_clients": [],  # Specific client IDs for early access
        "allowed_users": []     # Specific user IDs for testing
    },
    "assignment_notifications": {
        "enabled": True,
        "rollout_percentage": 50   # Enable notifications for 50% of users
    },
    "bulk_assignments": {
        "enabled": True,
        "rollout_percentage": 25   # Enable bulk operations for 25% of users
    }
}
```

## Monitoring and Alerting

### Performance Metrics

```yaml
# prometheus_alerts.yml
groups:
  - name: team_assignment_system
    rules:
      - alert: HighAssignmentLatency
        expr: assignment_operation_duration_seconds > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High assignment operation latency"
          
      - alert: TeamCreationFailures
        expr: rate(team_creation_failures_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High team creation failure rate"
          
      - alert: NotificationDeliveryFailures
        expr: rate(notification_delivery_failures_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High notification delivery failure rate"
```

### Health Checks

```python
# health_checks.py
async def check_team_assignment_system():
    """Health check for team assignment system"""
    checks = {
        "database": False,
        "cache": False,
        "notifications": False
    }
    
    try:
        # Test database connectivity
        await db.execute(text("SELECT 1 FROM teams LIMIT 1"))
        checks["database"] = True
        
        # Test cache
        cache_service.set("health_check", "ok")
        if cache_service.get("health_check") == "ok":
            checks["cache"] = True
        
        # Test notification system
        # This would test notification delivery capability
        checks["notifications"] = True
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
    
    return checks
```

## Rollback Procedures

### Database Rollback

```sql
-- rollback_team_assignment.sql
-- Rollback script for team assignment system

-- Drop notification system tables
DROP TABLE IF EXISTS notification_history CASCADE;
DROP TABLE IF EXISTS notification_preferences CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;

-- Drop enum types
DROP TYPE IF EXISTS notification_type CASCADE;
DROP TYPE IF EXISTS notification_status CASCADE;
DROP TYPE IF EXISTS notification_channel CASCADE;

-- Remove user table extensions (if needed)
-- ALTER TABLE users DROP COLUMN IF EXISTS primary_role;
-- ALTER TABLE users DROP COLUMN IF EXISTS secondary_roles;
-- ALTER TABLE users DROP COLUMN IF EXISTS is_contact_person;
```

### API Rollback

```bash
#!/bin/bash
# rollback_api.sh

set -e

echo "Rolling back Team Assignment System API..."

# Revert to previous version
docker tag worky-api:previous worky-api:latest
docker-compose down api
docker-compose up -d api

# Verify rollback
sleep 30
curl -f http://localhost:8007/health || exit 1

echo "API rollback completed!"
```

## Gradual Rollout Plan

### Phase 1: Internal Testing (Week 1)
- Deploy to staging environment
- Enable for internal team only
- Test all core functionality
- Monitor performance metrics
- Fix any critical issues

### Phase 2: Limited Production (Week 2)
- Deploy to production with 10% rollout
- Enable for selected pilot clients
- Monitor error rates and performance
- Collect user feedback
- Adjust based on findings

### Phase 3: Expanded Rollout (Week 3)
- Increase rollout to 50%
- Enable notifications for 25% of users
- Monitor notification delivery rates
- Test bulk operations with larger datasets
- Performance optimization if needed

### Phase 4: Full Rollout (Week 4)
- Enable for 100% of users
- Full notification system activation
- Complete bulk operations rollout
- Final performance validation
- Documentation updates

## Production Configuration

### Environment Variables

```bash
# Production environment variables
export TEAM_ASSIGNMENT_CACHE_TTL=900  # 15 minutes
export NOTIFICATION_BATCH_SIZE=100
export ASSIGNMENT_VALIDATION_TIMEOUT=5
export TEAM_MEMBER_LIMIT=200
export BULK_ASSIGNMENT_LIMIT=500
export PERFORMANCE_MONITORING=true
export CACHE_ENABLED=true
```

### Database Configuration

```sql
-- Production database optimizations
-- Increase connection pool size
ALTER SYSTEM SET max_connections = 200;

-- Optimize for team queries
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';

-- Enable query logging for monitoring
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;
```

### Nginx Configuration

```nginx
# nginx configuration for team assignment endpoints
location /api/v1/teams/ {
    proxy_pass http://worky-api;
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_key "$request_uri$request_body";
}

location /api/v1/assignments/ {
    proxy_pass http://worky-api;
    proxy_cache api_cache;
    proxy_cache_valid 200 2m;
}

location /api/v1/notifications/ {
    proxy_pass http://worky-api;
    # No caching for notifications
}
```

## Post-Deployment Validation

### Automated Tests

```bash
#!/bin/bash
# post_deployment_tests.sh

echo "Running post-deployment validation tests..."

# Test team creation
curl -X POST http://localhost:8007/api/v1/teams/ \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Team","project_id":"PRJ-001"}' || exit 1

# Test assignment creation
curl -X POST http://localhost:8007/api/v1/assignments/ \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_type":"task","entity_id":"TSK-001","user_id":"USR-001","assignment_type":"developer"}' || exit 1

# Test notification system
curl -X GET http://localhost:8007/api/v1/notifications/summary \
  -H "Authorization: Bearer $TEST_TOKEN" || exit 1

echo "All post-deployment tests passed!"
```

### Performance Validation

```python
# performance_validation.py
import asyncio
import time
import aiohttp

async def validate_performance():
    """Validate system performance after deployment"""
    
    async with aiohttp.ClientSession() as session:
        # Test team creation performance
        start_time = time.time()
        async with session.post('/api/v1/teams/', json={
            "name": "Performance Test Team",
            "project_id": "PRJ-001"
        }) as response:
            assert response.status == 201
        
        creation_time = time.time() - start_time
        assert creation_time < 2.0, f"Team creation too slow: {creation_time}s"
        
        # Test assignment performance
        start_time = time.time()
        async with session.post('/api/v1/assignments/', json={
            "entity_type": "task",
            "entity_id": "TSK-001",
            "user_id": "USR-001",
            "assignment_type": "developer"
        }) as response:
            assert response.status == 201
        
        assignment_time = time.time() - start_time
        assert assignment_time < 1.0, f"Assignment creation too slow: {assignment_time}s"
        
        print("Performance validation passed!")

if __name__ == "__main__":
    asyncio.run(validate_performance())
```

## Troubleshooting Guide

### Common Deployment Issues

#### Migration Failures
```bash
# Check migration status
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM alembic_version;"

# Manual migration fix
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f db/migrations/027_create_notification_system.sql
```

#### API Startup Issues
```bash
# Check API logs
docker logs worky-api

# Verify database connectivity
docker exec worky-api python -c "from app.db.base import engine; print('DB OK')"

# Check environment variables
docker exec worky-api env | grep -E "(DATABASE|CACHE|NOTIFICATION)"
```

#### Performance Issues
```bash
# Check system resources
docker stats worky-api

# Monitor database connections
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT count(*) FROM pg_stat_activity;"

# Clear cache if needed
curl -X DELETE http://localhost:8007/api/v1/performance/cache/clear \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Security Checklist

- [ ] All API endpoints require authentication
- [ ] Input validation is enabled
- [ ] SQL injection protection is active
- [ ] XSS protection is configured
- [ ] Rate limiting is enabled
- [ ] Audit logging is working
- [ ] HTTPS is enforced
- [ ] Database connections are encrypted

## Maintenance Schedule

### Daily
- Monitor error rates and performance metrics
- Check notification delivery success rates
- Review system health checks

### Weekly
- Analyze performance trends
- Review audit logs for security issues
- Update documentation if needed

### Monthly
- Performance optimization review
- Security audit
- Backup verification
- Capacity planning review

## Success Criteria

The deployment is considered successful when:

- [ ] All database migrations complete without errors
- [ ] API endpoints respond within performance targets
- [ ] UI components load and function correctly
- [ ] Notifications are delivered successfully
- [ ] No critical errors in logs for 24 hours
- [ ] Performance metrics meet targets
- [ ] Security scans pass
- [ ] User acceptance testing passes