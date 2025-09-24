# Cloud Native Application

A modern cloud-native microservices application built with containerization, API gateway, service mesh, and observability features.

## Architecture

This application demonstrates cloud-native principles including:

- **Microservices Architecture**: Loosely coupled services
- **Containerization**: Docker containers for all services
- **API Gateway**: Centralized API management with Kong
- **Service Discovery**: Consul for service registration
- **Load Balancing**: NGINX for traffic distribution
- **Monitoring**: Prometheus and Grafana for observability
- **Distributed Tracing**: Jaeger for request tracing
- **Configuration Management**: Environment-based config
- **Health Checks**: Kubernetes-style health endpoints
- **CI/CD Ready**: GitHub Actions workflows

## Services

### 1. User Service (Node.js)

- User registration and authentication
- JWT token management
- User profile management

### 2. Product Service (Python FastAPI)

- Product catalog management
- Inventory tracking
- Search functionality

### 3. Order Service (Go)

- Order processing
- Payment integration
- Order status tracking

### 4. API Gateway (Kong)

- Request routing
- Rate limiting
- Authentication
- Load balancing

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.9+
- Go 1.19+

### Development Setup

1. Clone the repository:

```bash
git clone https://github.com/kovendhan5/cloud-native.git
cd cloud-native
```

2. Start the infrastructure services:

```bash
docker-compose -f docker-compose.infrastructure.yml up -d
```

3. Start the application services:

```bash
docker-compose up -d
```

4. Access the services:

- API Gateway: http://localhost:8000
- User Service: http://localhost:3001
- Product Service: http://localhost:3002
- Order Service: http://localhost:3003
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Jaeger: http://localhost:16686

## API Documentation

### User Service Endpoints

- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

### Product Service Endpoints

- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get product by ID
- `POST /api/products` - Create new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Order Service Endpoints

- `POST /api/orders` - Create new order
- `GET /api/orders/{id}` - Get order by ID
- `GET /api/orders/user/{userId}` - Get user orders
- `PUT /api/orders/{id}/status` - Update order status

## Monitoring and Observability

### Metrics

- Application metrics exposed on `/metrics` endpoint
- Custom business metrics
- Infrastructure metrics via Prometheus

### Logging

- Structured JSON logging
- Centralized log aggregation
- Log correlation with trace IDs

### Tracing

- Distributed tracing with Jaeger
- Request correlation across services
- Performance monitoring

## Deployment

### Kubernetes

```bash
kubectl apply -f k8s/
```

### Cloud Platforms

- AWS EKS deployment scripts in `deploy/aws/`
- Azure AKS deployment scripts in `deploy/azure/`
- GCP GKE deployment scripts in `deploy/gcp/`

## Testing

### Unit Tests

```bash
# User Service
cd services/user-service && npm test

# Product Service
cd services/product-service && python -m pytest

# Order Service
cd services/order-service && go test ./...
```

### Integration Tests

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Load Testing

```bash
# Using k6
k6 run tests/load/api-load-test.js
```

## Security

- JWT-based authentication
- HTTPS/TLS encryption
- CORS configuration
- Input validation
- Secret management
- Container security scanning

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

---

## Windows Quickstart (cmd.exe)

Use these commands in a plain `cmd` shell. Ensure Docker Desktop is running first (icon says "Docker Desktop is running").

```cmd
REM Clone
git clone https://github.com/kovendhan5/cloud-native.git
cd cloud-native

REM Copy sample env if you create one (optional)
REM type .env.example > .env

REM Start infrastructure (Mongo, Kong, Prometheus, Grafana, Jaeger, Consul)
docker compose -f docker-compose.infrastructure.yml up -d

REM Start application services (user, product, order)
docker compose up -d

REM List containers
docker compose ps

REM Tail logs for all
docker compose logs -f --tail=50
```

### Health Checks

```cmd
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health
curl http://localhost:8000/api/users/health
```

### Observability UIs

| Component  | URL                    |
| ---------- | ---------------------- |
| Prometheus | http://localhost:9090  |
| Grafana    | http://localhost:3000  |
| Jaeger     | http://localhost:16686 |
| Kong Admin | http://localhost:8001  |

### Tear Down

```cmd
docker compose down
docker compose -f docker-compose.infrastructure.yml down
```

## Troubleshooting (Windows)

| Symptom                                  | Cause                           | Fix                                                                |
| ---------------------------------------- | ------------------------------- | ------------------------------------------------------------------ | ------------------------------------------ |
| `open //./pipe/dockerDesktopLinuxEngine` | Docker engine not started       | Launch Docker Desktop and wait until running                       |
| Healthcheck failing for order-service    | `wget` missing (fixed)          | Rebuild image: `docker compose build order-service`                |
| `port already allocated`                 | Port in use                     | `netstat -ano                                                      | findstr :3001`then`taskkill /PID <pid> /F` |
| Mongo auth errors                        | Wrong URI or authSource missing | Use `mongodb://admin:password@mongodb:27017/<db>?authSource=admin` |
| Kong route 404                           | Path mismatch                   | Check `infrastructure/kong.yml` paths and container logs           |

### Check Docker Engine

```cmd
docker info >NUL 2>&1 || echo Docker engine not reachable
```

### Rebuild Only One Service

```cmd
docker compose build product-service
docker compose up -d product-service
```

### View Structured Logs

```cmd
docker compose logs -f user-service
docker compose logs -f product-service
docker compose logs -f order-service
```

### Metrics Endpoints

```cmd
curl http://localhost:3001/metrics | more
curl http://localhost:3002/metrics | more
curl http://localhost:3003/metrics | more
```

## Helper Scripts (Optional)

Create a `scripts` folder (not yet committed) and drop these `.cmd` files for convenience.

`scripts\up-all.cmd`

```cmd
@echo off
echo Starting infrastructure...
docker compose -f docker-compose.infrastructure.yml up -d || goto :error
echo Starting application services...
docker compose up -d || goto :error
docker compose ps
echo All services started.
goto :eof
:error
echo Failed (errorlevel=%errorlevel%)
exit /b %errorlevel%
```

`scripts\down-all.cmd`

```cmd
@echo off
docker compose down
docker compose -f docker-compose.infrastructure.yml down
echo Stacks stopped.
```

`scripts\health.cmd`

```cmd
@echo off
for %%U in (3001 3002 3003) do (
	echo Checking service on port %%U...
	curl -s http://localhost:%%U/health || echo Failed: %%U
	echo.
)
curl -s http://localhost:8000/api/users/health
```

---

_Additional Windows-focused guidance appended on: 2025-09-24._
