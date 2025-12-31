# Worky Deployment Guide for Contabo

This guide will help you deploy the Worky application to a Contabo VPS server.

## Prerequisites

1. **Contabo VPS Server** with:
   - Ubuntu 20.04+ or Debian 11+
   - At least 2GB RAM (4GB recommended)
   - Docker and Docker Compose installed
   - Domain name configured (optional but recommended)

2. **Domain Configuration** (if using custom domain):
   - DNS A record pointing to your Contabo server IP
   - SSL certificate (Let's Encrypt recommended)

## Pre-Deployment Checklist

### ⚠️ CRITICAL: Before deploying, ensure you:

- [ ] Change all default passwords
- [ ] Generate a strong SECRET_KEY
- [ ] Update CORS_ORIGINS with your domain
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Configure monitoring/logging

## Step 1: Server Setup

### 1.1 Connect to your Contabo server

```bash
ssh root@your-server-ip
```

### 1.2 Update system packages

```bash
apt update && apt upgrade -y
```

### 1.3 Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Add your user to docker group (if not root)
usermod -aG docker $USER
```

### 1.4 Install Nginx (if not using Docker nginx)

```bash
apt install nginx certbot python3-certbot-nginx -y
```

### 1.5 Configure Firewall

```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

## Step 2: Application Deployment

### 2.1 Clone or upload your application

```bash
# Option 1: Clone from Git
git clone <your-repo-url> /opt/worky
cd /opt/worky

# Option 2: Upload via SCP
# scp -r /path/to/worky root@your-server:/opt/worky
```

### 2.2 Create production environment file

```bash
cp .env.production.example .env.production
nano .env.production
```

**Update these critical values:**

```bash
# Generate a strong secret key
# Run: openssl rand -hex 32
SECRET_KEY=your-generated-secret-key-here

# Strong database password
DATABASE_PASSWORD=your-strong-db-password-here

# Your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2.3 Build UI for production

**Important**: The UI has been updated to handle environment variables safely. The application will work correctly on first load without requiring manual file edits.

```bash
# Option 1: Use the build script (recommended)
./scripts/build-ui-prod.sh

# Option 2: Manual build
cd ui
npm install
npm run build
cd ..
```

**Note**: The UI build process is now robust and handles environment variable initialization correctly. The `queryClient.ts` file has been updated to safely handle cases where `import.meta.env.MODE` might not be immediately available, ensuring the application works on first load on new devices.

### 2.4 Update nginx configuration

Edit `nginx/conf.d/worky.conf` and replace:
- `yourdomain.com` with your actual domain
- Update SSL certificate paths if using Let's Encrypt

### 2.5 Set up SSL certificates (Let's Encrypt)

```bash
# If using standalone certbot
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx/ssl directory
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

### 2.6 Start services

```bash
# Use production docker-compose
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

### 2.7 Verify deployment

```bash
# Check containers
docker ps

# Check logs
docker logs worky-api-prod
docker logs worky-nginx-prod

# Test API
curl http://localhost/api/health

# Test UI
curl http://localhost
```

## Step 3: Post-Deployment Configuration

### 3.1 Database Backups

Create a backup script:

```bash
cat > /opt/worky/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/worky/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker exec worky-postgres-prod pg_dump -U worky_user worky > $BACKUP_DIR/worky_$DATE.sql
gzip $BACKUP_DIR/worky_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
EOF

chmod +x /opt/worky/backup-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/worky/backup-db.sh") | crontab -
```

### 3.2 Monitoring

Set up log rotation:

```bash
cat > /etc/logrotate.d/worky << 'EOF'
/opt/worky/volumes/api-logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### 3.3 Auto-restart on reboot

Create systemd service (optional):

```bash
cat > /etc/systemd/system/worky.service << 'EOF'
[Unit]
Description=Worky Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/worky
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl enable worky
systemctl start worky
```

## Step 4: Security Hardening

### 4.1 Update default admin password

After first login, change the default admin password:
- Email: `admin@datalegos.com`
- Default password: `password` (CHANGE THIS IMMEDIATELY)

### 4.2 Database security

- Database is not exposed externally (good)
- Ensure strong password is set
- Consider IP whitelisting if needed

### 4.3 API security

- SECRET_KEY is set (good)
- CORS is configured (good)
- Consider rate limiting for production

## Troubleshooting

### Issue: Containers won't start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check environment variables
docker-compose -f docker-compose.prod.yml config
```

### Issue: Database connection errors

```bash
# Check database container
docker logs worky-postgres-prod

# Test connection
docker exec worky-postgres-prod psql -U worky_user -d worky -c "SELECT 1;"
```

### Issue: SSL certificate errors

```bash
# Renew Let's Encrypt certificate
certbot renew

# Restart nginx
docker restart worky-nginx-prod
```

### Issue: UI not loading

```bash
# Check if UI is built
ls -la ui/dist

# Rebuild UI
cd ui && npm run build && cd ..
docker restart worky-nginx-prod
```

### Issue: UI shows error screen on first load (new devices)

**This issue has been fixed!** The `queryClient.ts` file now safely handles environment variable initialization. If you still encounter this:

1. **Clear browser cache** and reload
2. **Verify the build** includes the latest queryClient.ts fix:
   ```bash
   grep -A 5 "isDevelopment" ui/src/lib/queryClient.ts
   ```
3. **Rebuild UI** to ensure latest code is included:
   ```bash
   cd ui && npm run build && cd ..
   docker restart worky-nginx-prod
   ```

## Maintenance

### Update application

```bash
cd /opt/worky
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### View logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker logs worky-api-prod -f
```

### Database migrations

Migrations run automatically on first start. For manual migration:

```bash
docker exec worky-api-prod python -m alembic upgrade head
```

## Support

For issues or questions:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify environment variables: `.env.production`
3. Check container health: `docker ps`

## Production Checklist

Before going live, ensure:

- [x] All passwords changed from defaults
- [x] SECRET_KEY is strong and unique
- [x] CORS_ORIGINS configured correctly
- [x] SSL certificates installed and valid
- [x] Database backups configured
- [x] Firewall rules configured
- [x] Monitoring/logging set up
- [x] UI built for production
- [x] Environment set to "production"
- [x] Default admin password changed
- [x] Database not exposed externally

