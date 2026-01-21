# Shared Data Folder Strategy for Worky Application

## 📋 Data Types to Store in Shared Folders

### 1. **PostgreSQL Database Data**
- **What**: All database files (tables, indexes, WAL files)
- **Why**: Prevents data loss when containers are rebuilt or stopped
- **Risk if not shared**: Complete data loss on container removal

### 2. **User-Generated Files**
- **What**: Bug attachments, test case files, comment attachments, user avatars (future)
- **Why**: User uploads persist across container rebuilds
- **Risk if not shared**: All uploaded files lost on container rebuild

### 3. **Application Logs**
- **What**: API logs, error logs, activity logs
- **Why**: Accessible without entering containers, persists across restarts
- **Risk if not shared**: Logs lost on container restart, harder debugging

### 4. **Generated Reports**
- **What**: PDF/CSV exports, analytics reports
- **Why**: Users can download reports even after container rebuilds
- **Risk if not shared**: Generated reports lost

### 5. **Backup Data**
- **What**: Database dumps, snapshots
- **Why**: Independent backup location for disaster recovery
- **Risk if not shared**: No easy way to restore if database corrupts

### 6. **Configuration Files** (Optional)
- **What**: Environment files, nginx configs
- **Why**: Edit configs without rebuilding images
- **Risk if not shared**: Need to rebuild containers for config changes

---

## 📁 Proposed Folder Structure

### Development (Relative Path)
```
../shared_data/
├── database/
│   └── postgres-data/          # PostgreSQL data directory
├── uploads/
│   ├── bugs/                   # Bug attachments
│   ├── test-cases/             # Test case attachments
│   └── comments/               # Comment attachments
├── logs/
│   └── api-logs/               # API application logs
├── exports/
│   └── reports/                # Generated reports (PDF, CSV)
└── backups/
    └── database/               # Database backup files
```

### Production (Absolute Path)
```
/opt/shared_data/
├── database/
│   └── postgres-data/
├── uploads/
│   ├── bugs/
│   ├── test-cases/
│   └── comments/
├── logs/
│   └── api-logs/
├── exports/
│   └── reports/
└── backups/
    └── database/
```

---

## 🔧 Docker Compose Configuration

### Development (`docker-compose.yml`)
```yaml
services:
  db:
    volumes:
      - ../shared_data/database/postgres-data:/var/lib/postgresql/data
      - ./db/migrations:/docker-entrypoint-initdb.d
  
  api:
    volumes:
      - ../shared_data/logs/api-logs:/app/logs
      - ../shared_data/uploads:/app/uploads
      - ../shared_data/exports:/app/exports
```

### Production (`docker-compose.prod.yml`)
```yaml
services:
  db:
    volumes:
      - /opt/shared_data/database/postgres-data:/var/lib/postgresql/data
      - ./db/migrations:/docker-entrypoint-initdb.d
  
  api:
    volumes:
      - /opt/shared_data/logs/api-logs:/app/logs
      - /opt/shared_data/uploads:/app/uploads
      - /opt/shared_data/exports:/app/exports
```

---

## 🔒 Best Practices

### Security & Permissions
- **Database**: Owned by postgres user (UID 999) with 700 permissions
- **Uploads**: Owned by API container user with 755 permissions
- **Logs**: Writable by API container, readable by admins
- **Secrets**: Keep `.env` files outside git, use 600 permissions

### Environment Separation
- **Development**: `../shared_data_dev/` or `D:\shared_data_dev\`
- **Staging**: `../shared_data_staging/`
- **Production**: `/opt/shared_data/` (absolute path)

### Backups & Disaster Recovery
- **Daily**: Automated `pg_dump` to `backups/database/`
- **Weekly**: Copy entire `shared_data` folder to external storage
- **Test**: Regularly test restore procedures
- **Retention**: Keep 30 days of daily backups, 12 months of weekly backups

### Scalability
- **Current**: Bind mounts work for single server
- **Future**: Can migrate to NFS/EFS for multi-server setup
- **Migration**: Same folder structure, just change mount point

---

## 📝 Implementation Checklist

- [ ] Create `shared_data` folder structure
- [ ] Update `docker-compose.yml` volumes
- [ ] Update `docker-compose.prod.yml` volumes
- [ ] Add file storage environment variables
- [ ] Create `FileService` class for uploads
- [ ] Implement file upload endpoints
- [ ] Update shell scripts to create folders
- [ ] Test migration on development
- [ ] Document backup procedures
- [ ] Perform production migration (with backup)
- [ ] Verify all operations work
- [ ] Remove old `volumes/` folder

---

## ⚠️ Important Notes

1. **PostgreSQL**: Only mount ONE volume to `/var/lib/postgresql/data` - never multiple mounts
2. **Migration**: Always backup existing data before moving
3. **Permissions**: Ensure Docker containers can read/write to shared folders
4. **Testing**: Test on development environment first
5. **Rollback**: Keep old `volumes/` folder until migration verified

---

## 🚀 Migration Steps

1. Stop all containers: `docker compose down`
2. Create `shared_data` folder structure
3. Copy existing data:
   - `volumes/postgres-data/` → `shared_data/database/postgres-data/`
   - `volumes/api-logs/` → `shared_data/logs/api-logs/`
4. Update `docker-compose.yml` volumes
5. Start containers: `docker compose up -d`
6. Verify everything works
7. Delete old `volumes/` folder (after verification)

---

**Status**: Plan ready, implementation pending

