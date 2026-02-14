# Deployment Guide

This guide covers deploying Simple Dash to production environments.

## Prerequisites

- Server with Docker installed (Ubuntu 22.04+ recommended)
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)
- Reverse proxy (nginx recommended)

## Deployment Options

### Option 1: Docker Compose (Recommended)

Simplest method for single-server deployments.

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose (if not included)
sudo apt install docker-compose-plugin
```

#### Step 2: Deploy Application

```bash
# Clone repository
git clone https://github.com/derekology/simpledash.git
cd simpledash

# Configure environment
cp .env.example .env
nano .env  # Edit as needed

# Build and start
docker compose up -d

# Check status
docker compose ps
docker compose logs
```

#### Step 3: Set Up Reverse Proxy

**Install nginx:**

```bash
sudo apt install nginx
```

**Create nginx configuration:**

```bash
sudo nano /etc/nginx/sites-available/simpledash
```

**Add configuration:**

```nginx
server {
    listen 80;
    server_name dash.example.com;

    # Increase upload size limits
    client_max_body_size 120M;
    client_body_timeout 300s;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for large file uploads
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/simpledash /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 4: SSL/TLS Setup

**Install Certbot:**

```bash
sudo apt install certbot python3-certbot-nginx
```

**Get certificate:**

```bash
sudo certbot --nginx -d dash.example.com
```

**Auto-renewal:**

```bash
# Test renewal
sudo certbot renew --dry-run

# Renewal happens automatically via systemd timer
sudo systemctl status certbot.timer
```

### Option 2: Build from Source

For customized deployments.

```bash
# Build frontend
cd frontend
npm ci
npm run build

# Set up Python environment
cd ..
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Option 3: Cloud Platforms

#### AWS ECS

1. Push Docker image to ECR
2. Create ECS task definition
3. Create ECS service with ALB
4. Configure Route53 for DNS

#### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/simpledash

# Deploy
gcloud run deploy simpledash \
  --image gcr.io/PROJECT_ID/simpledash \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --max-instances 10
```

#### DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build settings
3. Set environment variables
4. Deploy

## Configuration

### Environment Variables

Production-ready `.env` file:

```env
# Server
PORT=8000

# Upload Limits
MAX_FILE_SIZE=10485760  # 10MB
MAX_FILES=12

# Security
# Add any API keys or secrets here
```

### Reverse Proxy Configuration

Complete nginx configuration with security headers:

```nginx
server {
    listen 443 ssl http2;
    server_name dash.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/dash.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dash.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Upload limits
    client_max_body_size 120M;
    client_body_timeout 300s;
    client_header_timeout 300s;

    # Proxy configuration
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_buffering off;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name dash.example.com;
    return 301 https://$server_name$request_uri;
}
```

## Security Considerations

### 1. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. Container Security

- Run as non-root user (already configured in Dockerfile)
- Keep base images updated
- Scan for vulnerabilities: `docker scout cves simpledash`

### 3. Application Security

- Files are processed but not stored persistently
- Implement rate limiting at nginx level
- Monitor for unusual upload patterns

### 4. Rate Limiting (nginx)

```nginx
http {
    limit_req_zone $binary_remote_addr zone=upload:10m rate=5r/m;

    server {
        # ... other config

        location /parse {
            limit_req zone=upload burst=2;
            proxy_pass http://localhost:8000;
        }
    }
}
```

## Monitoring

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check container health
docker inspect --format='{{.State.Health.Status}}' simpledash
```

### Logging

```bash
# View real-time logs
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100

# Follow specific service
docker compose logs -f simpledash
```

### System Monitoring

```bash
# Container resource usage
docker stats simpledash

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Backup and Recovery

### Backup Strategy

Simple Dash doesn't store data persistently, but you should backup:

1. Configuration files (`.env`, `docker-compose.yml`)
2. Custom nginx configuration
3. SSL certificates (handled by certbot)

```bash
# Backup configuration
tar -czf simpledash-config-$(date +%Y%m%d).tar.gz .env docker-compose.yml
```

## Scaling

### Horizontal Scaling

Run multiple instances behind a load balancer:

```yaml
# docker-compose.yml
services:
  simpledash-1:
    build: .
    container_name: simpledash-1
    ports:
      - "8001:8000"

  simpledash-2:
    build: .
    container_name: simpledash-2
    ports:
      - "8002:8000"
```

**nginx load balancer:**

```nginx
upstream simpledash {
    server localhost:8001;
    server localhost:8002;
}

server {
    location / {
        proxy_pass http://simpledash;
    }
}
```

### Vertical Scaling

Adjust resource limits:

```yaml
services:
  simpledash:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
```

## Updates and Maintenance

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d

# Verify
docker compose ps
docker compose logs
```

### Update Dependencies

```bash
# Update Python dependencies
pip list --outdated
# Update requirements.txt as needed

# Update Node dependencies
cd frontend
npm outdated
# Update package.json as needed
```

### Zero-Downtime Updates

```bash
# Build new image
docker compose build

# Start new container on different port
docker compose up -d --scale simpledash=2

# Update nginx to use new instance
# Update docker-compose to use new image
# Stop old container
```

## Troubleshooting

### Common Issues

**1. Container won't start**

```bash
docker compose logs
# Check port conflicts
sudo netstat -tulpn | grep 8000
```

**2. 502 Bad Gateway**

```bash
# Check if container is running
docker compose ps

# Check nginx configuration
sudo nginx -t
```

**3. File upload fails**

```bash
# Check nginx upload size
grep client_max_body_size /etc/nginx/sites-available/simpledash

# Check container logs
docker compose logs | grep -i error
```

**4. High memory usage**

```bash
# Check container stats
docker stats simpledash

# Restart container
docker compose restart
```

## Performance Optimization

### Nginx Caching

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Gzip Compression

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

## Support

For deployment issues:

- Check logs: `docker compose logs`
- Review nginx logs: `/var/log/nginx/error.log`
- Test configuration: `nginx -t`
- Check Docker status: `docker compose ps`
