# Windows Quick Start Guide

## Prerequisites

1. **Docker Desktop** - Must be installed and running

   - Download from: https://www.docker.com/products/docker-desktop
   - Start Docker Desktop and wait for it to be ready

2. **Git Bash or Command Prompt** - For running commands

3. **curl** (optional) - For testing endpoints
   - Included in Windows 10 1803+ and Windows 11
   - Or use PowerShell's `Invoke-WebRequest`

## Quick Start (Windows Command Prompt)

### 1. Start All Services

```cmd
start.bat
```

This will:

- Start infrastructure (MongoDB, Kong, Prometheus, Grafana, Jaeger, Consul)
- Wait 10 seconds for infrastructure to be ready
- Start application services (User, Product, Order)

### 2. Check Service Health

```cmd
check-health.bat
```

### 3. View Logs

```cmd
REM All services
logs.bat

REM Specific service
logs.bat user-service
logs.bat product-service
logs.bat order-service
```

### 4. Stop All Services

```cmd
stop.bat
```

## Manual Commands

### Start Infrastructure Only

```cmd
docker compose -f docker-compose.infrastructure.yml up -d
```

### Start Application Services

```cmd
docker compose up -d
```

### Check Status

```cmd
docker compose ps
docker compose -f docker-compose.infrastructure.yml ps
```

### View Logs

```cmd
docker compose logs -f user-service
docker compose logs -f product-service
docker compose logs -f order-service
```

### Stop Services

```cmd
docker compose down
docker compose -f docker-compose.infrastructure.yml down
```

### Remove Volumes (Clean Slate)

```cmd
docker compose down -v
docker compose -f docker-compose.infrastructure.yml down -v
```

## Service URLs

After starting services, access them at:

- **Kong API Gateway**: http://localhost:8000
- **Kong Admin API**: http://localhost:8001
- **User Service**: http://localhost:3001
- **Product Service**: http://localhost:3002
- **Order Service**: http://localhost:3003
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (login: admin/admin)
- **Jaeger**: http://localhost:16686
- **Consul**: http://localhost:8500

## Testing Endpoints

### Health Checks

```cmd
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health
```

### Register a User

```cmd
curl -X POST http://localhost:8000/api/users/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"john_doe\",\"email\":\"john@example.com\",\"password\":\"password123\",\"firstName\":\"John\",\"lastName\":\"Doe\"}"
```

### Login

```cmd
curl -X POST http://localhost:8000/api/users/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"john@example.com\",\"password\":\"password123\"}"
```

### Get Products

```cmd
curl http://localhost:8000/api/products
```

## Troubleshooting

### Docker Not Running

**Error**: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`

**Solution**: Start Docker Desktop and wait until it shows "Docker Desktop is running"

### Port Already in Use

**Error**: `port is already allocated`

**Solution**: Check what's using the port

```cmd
netstat -ano | findstr :3001
netstat -ano | findstr :8000
```

Kill the process or change ports in `docker-compose.yml`

### Services Not Healthy

Check logs:

```cmd
docker compose logs user-service
docker compose logs product-service
docker compose logs order-service
docker compose logs mongodb
```

### Cannot Connect to MongoDB

Ensure infrastructure is running:

```cmd
docker compose -f docker-compose.infrastructure.yml ps
```

Restart if needed:

```cmd
docker compose -f docker-compose.infrastructure.yml restart mongodb
```

### Build Errors

Clean rebuild:

```cmd
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Development Workflow

### Rebuild Specific Service

```cmd
docker compose build user-service
docker compose up -d user-service
```

### View Real-Time Logs

```cmd
docker compose logs -f user-service
```

### Execute Commands in Container

```cmd
docker exec -it user-service /bin/sh
docker exec -it mongodb mongosh
```

### Reset Everything

```cmd
docker compose down -v
docker compose -f docker-compose.infrastructure.yml down -v
docker system prune -a
start.bat
```

## Next Steps

1. Review `README.md` for API documentation
2. Review `SETUP.md` for detailed configuration
3. Check Grafana dashboards at http://localhost:3000
4. Monitor metrics at http://localhost:9090
5. View traces at http://localhost:16686
