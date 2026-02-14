# Docker Setup Guide

This guide explains how to run Simple Dash using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose V2 (comes with Docker Desktop)

## Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/derekology/simpledash.git
   cd simpledash
   ```

2. **Create environment file (optional)**

   ```bash
   cp .env.example .env
   # Edit .env to customize settings if needed
   ```

3. **Build and start the container**

   ```bash
   docker compose up -d
   ```

4. **Access the application**
   - Open your browser to `http://localhost:8000`

## Using the Makefile

For convenience, use the included Makefile:

```bash
# Build the Docker image
make build

# Start the container
make up

# View logs
make logs

# Stop the container
make down

# Restart the container
make restart

# Rebuild and restart
make rebuild

# Open a shell in the container
make shell

# Check container health
make health

# Clean up everything
make clean
```

## Environment Variables

Configure the application using environment variables:

| Variable        | Default    | Description                           |
| --------------- | ---------- | ------------------------------------- |
| `PORT`          | `8000`     | Server port                           |
| `MAX_FILE_SIZE` | `10485760` | Maximum file size in bytes (10MB)     |
| `MAX_FILES`     | `12`       | Maximum files per upload              |
| `DEV`           | `False`    | Development mode (enables CORS, etc.) |

### Setting Environment Variables

#### Option 1: .env file

Create a `.env` file in the project root:

```env
PORT=8000
MAX_FILE_SIZE=10485760
MAX_FILES=12
```

#### Option 2: Command line

```bash
PORT=9000 docker compose up -d
```

#### Option 3: docker-compose.yml

Edit the `environment` section in `docker-compose.yml`.

## Docker Commands

### Basic Operations

```bash
# Build the image
docker compose build

# Start in foreground (see logs)
docker compose up

# Start in background (detached)
docker compose up -d

# Stop the container
docker compose down

# View logs
docker compose logs -f

# Restart
docker compose restart

# Check status
docker compose ps
```

### Maintenance

```bash
# Open shell in running container
docker compose exec simpledash sh

# View resource usage
docker stats simpledash

# Inspect container
docker inspect simpledash

# Check health
docker compose ps
```

## Production Deployment

### Using a Reverse Proxy

For production, place Simple Dash behind a reverse proxy like nginx:

```nginx
server {
    listen 80;
    server_name dash.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase limits for file uploads
        client_max_body_size 120M;
        proxy_read_timeout 300s;
    }
}
```

### SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d dash.example.com
```

### Security Best Practices

1. **Run behind a reverse proxy** with SSL/TLS
2. **Limit upload sizes** at the proxy level
3. **Use firewall rules** to restrict access
4. **Keep Docker updated** for security patches
5. **Monitor logs** for suspicious activity

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs

# Check if port is already in use
netstat -tulpn | grep 8000

# Try a different port
PORT=9000 docker compose up
```

### Build failures

```bash
# Clean build cache
docker compose build --no-cache

# Check Docker disk space
docker system df

# Clean up unused images
docker system prune
```

### Frontend not loading

```bash
# Rebuild frontend
docker compose build --no-cache

# Check if dist folder exists
docker compose exec simpledash ls -la frontend/

# Check logs for errors
docker compose logs | grep -i error
```

### Health check failing

```bash
# Check health status
docker inspect --format='{{json .State.Health}}' simpledash | jq

# Test health endpoint manually
docker compose exec simpledash python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/docs').read())"
```

## Architecture

### Multi-stage Build

The Dockerfile uses a multi-stage build process:

1. **Frontend Builder** (Node 20 Alpine)
   - Installs npm dependencies
   - Builds Vue.js frontend
   - Outputs to `dist/`

2. **Backend Builder** (Python 3.11 Slim)
   - Installs Python dependencies
   - Prepares FastAPI backend

3. **Production** (Python 3.11 Slim)
   - Minimal final image
   - Non-root user for security
   - Only runtime dependencies

### Image Size

- Frontend builder: ~200MB (discarded)
- Backend builder: ~150MB (discarded)
- Final image: ~250MB

## Advanced Configuration

### Custom Port Binding

Bind to a specific network interface:

```yaml
ports:
  - "127.0.0.1:8000:8000" # Only localhost
  - "0.0.0.0:8000:8000" # All interfaces
```

### Resource Limits

Add resource constraints in `docker-compose.yml`:

```yaml
services:
  simpledash:
    # ... other config
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
        reservations:
          memory: 256M
```

### Health Check Tuning

Adjust health check parameters:

```yaml
healthcheck:
  interval: 30s # Check every 30 seconds
  timeout: 5s # Timeout after 5 seconds
  retries: 3 # Mark unhealthy after 3 failures
  start_period: 10s # Grace period on startup
```

## Development with Docker

### Development Mode

For development with hot-reload:

```bash
# Start backend in dev mode
docker compose run --rm -p 8000:8000 simpledash uvicorn app.main:app --host 0.0.0.0 --reload

# In another terminal, run frontend dev server on host
cd frontend
npm install
npm run dev
```

### Volume Mounting for Development

Add volume mounts in docker-compose.yml for development:

```yaml
volumes:
  - ./app:/app/app
  - ./frontend/src:/app/frontend/src
```

## Support

For issues or questions:

- Check the logs: `docker compose logs`
- Open an issue on GitHub
- Review FastAPI docs at `http://localhost:8000/docs`
