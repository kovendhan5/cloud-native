# Cloud Native Application

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database
MONGODB_URI=mongodb://admin:password@localhost:27017

# JWT Secret
JWT_SECRET=your-super-secret-jwt-key-here-minimum-32-characters

# Service Ports
USER_SERVICE_PORT=3001
PRODUCT_SERVICE_PORT=3002
ORDER_SERVICE_PORT=3003

# API Gateway
KONG_ADMIN_PORT=8001
KONG_PROXY_PORT=8000

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
JAEGER_PORT=16686

# Consul
CONSUL_PORT=8500

# Environment
NODE_ENV=development
ENVIRONMENT=development
GIN_MODE=debug
```

## Quick Start Commands

### Development Mode

1. **Start infrastructure services:**

```bash
docker-compose -f docker-compose.infrastructure.yml up -d
```

2. **Install dependencies:**

```bash
# User Service
cd services/user-service && npm install

# Product Service
cd services/product-service && pip install -r requirements.txt

# Order Service
cd services/order-service && go mod download
```

3. **Run services locally:**

```bash
# Terminal 1 - User Service
cd services/user-service && npm run dev

# Terminal 2 - Product Service
cd services/product-service && uvicorn main:app --reload --port 3002

# Terminal 3 - Order Service
cd services/order-service && go run main.go
```

### Production Mode (Docker)

1. **Start all services:**

```bash
docker-compose -f docker-compose.infrastructure.yml up -d
docker-compose up -d
```

2. **Check service health:**

```bash
curl http://localhost:3001/health  # User Service
curl http://localhost:3002/health  # Product Service
curl http://localhost:3003/health  # Order Service
```

### Kubernetes Deployment

1. **Create namespace and secrets:**

```bash
kubectl apply -f k8s/secrets.yaml
```

2. **Deploy database:**

```bash
kubectl apply -f k8s/mongodb.yaml
```

3. **Deploy services:**

```bash
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/product-service.yaml
kubectl apply -f k8s/order-service.yaml
```

4. **Check deployment:**

```bash
kubectl get pods -n cloud-native
kubectl get services -n cloud-native
```

## API Testing

### User Service Examples

```bash
# Register a new user
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "firstName": "John",
    "lastName": "Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'

# Get profile (requires token)
curl -X GET http://localhost:8000/api/users/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Product Service Examples

```bash
# Create a product
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "category": "Electronics",
    "inventory": 50,
    "sku": "LAP001"
  }'

# Get all products
curl -X GET http://localhost:8000/api/products

# Search products
curl -X GET "http://localhost:8000/api/products/search?q=laptop"
```

### Order Service Examples

```bash
# Create an order
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "items": [
      {
        "product_id": "64f8a1b2c3d4e5f6g7h8i9j0",
        "name": "Laptop",
        "price": 999.99,
        "quantity": 1
      }
    ]
  }'

# Get order by ID
curl -X GET http://localhost:8000/api/orders/ORDER_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Update order status
curl -X PUT http://localhost:8000/api/orders/ORDER_ID/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"status": "confirmed"}'
```

## Monitoring and Observability

### Prometheus Metrics

- **User Service**: http://localhost:3001/metrics
- **Product Service**: http://localhost:3002/metrics
- **Order Service**: http://localhost:3003/metrics
- **Prometheus UI**: http://localhost:9090

### Grafana Dashboards

- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: admin

### Jaeger Tracing

- **URL**: http://localhost:16686

### Kong Admin API

- **URL**: http://localhost:8001

## Troubleshooting

### Common Issues

1. **Port conflicts:**

   - Check if ports are already in use: `netstat -an | findstr "3001"`
   - Stop conflicting services or change ports

2. **Database connection errors:**

   - Ensure MongoDB is running: `docker-compose ps`
   - Check connection string in environment variables

3. **JWT token issues:**

   - Ensure JWT_SECRET is set consistently across services
   - Check token expiration time

4. **Docker build failures:**
   - Clear Docker cache: `docker system prune -a`
   - Check Dockerfile syntax and base image availability

### Logs

```bash
# View service logs
docker-compose logs -f user-service
docker-compose logs -f product-service
docker-compose logs -f order-service

# Kubernetes logs
kubectl logs -f deployment/user-service -n cloud-native
kubectl logs -f deployment/product-service -n cloud-native
kubectl logs -f deployment/order-service -n cloud-native
```

## Security Considerations

1. **Change default passwords** in production
2. **Use strong JWT secrets** (minimum 32 characters)
3. **Enable HTTPS** in production environments
4. **Implement proper RBAC** for Kubernetes
5. **Scan container images** for vulnerabilities
6. **Use secrets management** tools in production

## Performance Tuning

1. **Database indexing** for frequently queried fields
2. **Connection pooling** for database connections
3. **Caching strategies** (Redis/Memcached)
4. **Load balancing** with multiple service instances
5. **Resource limits** in Kubernetes deployments
