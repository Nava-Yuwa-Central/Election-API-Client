# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed on your server
- Git installed
- Domain name (optional, for production)

## Deployment Steps

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd nepal-entity-service-fastapi
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your production values:

```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=nepal_entity_db
POSTGRES_PORT=5432

DATABASE_URL=postgresql://your_user:your_secure_password@postgres:5432/nepal_entity_db

HOST=0.0.0.0
PORT=8195
LOG_LEVEL=INFO

REDIS_URL=redis://localhost:6379/0
CACHE_EXPIRY=3600
```

### 3. Start the Services

```bash
docker compose up -d
```

### 4. Verify Deployment

```bash
# Check if containers are running
docker compose ps

# Check API health
curl http://localhost:8195/health

# View logs
docker compose logs -f api
```

### 5. Access the API

- API: http://your-server-ip:8195
- API Documentation: http://your-server-ip:8195/docs
- Alternative Docs: http://your-server-ip:8195/redoc

## Production Considerations

### 1. Use a Reverse Proxy (Nginx/Caddy)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8195;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Enable SSL/TLS

Use Let's Encrypt with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

### 3. Database Backups

Set up automated PostgreSQL backups:

```bash
# Create backup script
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker compose exec -T postgres pg_dump -U nesuser nepal_entity_db > $BACKUP_DIR/backup_$TIMESTAMP.sql
```

### 4. Monitoring

Use Docker health checks and monitoring tools:

```bash
# View container health status
docker compose ps

# Monitor resource usage
docker stats
```

### 5. Update and Maintenance

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
docker compose up -d --build

# Run database migrations
docker compose exec api alembic upgrade head
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker compose logs postgres

# Test database connection
docker compose exec postgres psql -U nesuser -d nepal_entity_db -c "SELECT version();"
```

### API Not Responding

```bash
# Check API logs
docker compose logs api

# Restart API container
docker compose restart api
```

### Port Already in Use

Change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8196:8195"  # Changed external port to 8196
```

## Security Recommendations

1. Change default PostgreSQL credentials
2. Use strong passwords
3. Enable firewall rules
4. Keep Docker and system packages updated
5. Use SSL/TLS for all connections
6. Implement rate limiting
7. Regular security audits
8. Monitor logs for suspicious activity

## Scaling

For horizontal scaling, consider:

1. Use PostgreSQL connection pooling (PgBouncer)
2. Deploy multiple API instances behind a load balancer
3. Implement Redis for caching
4. Use managed PostgreSQL service for high availability
