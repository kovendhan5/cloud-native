@echo off
REM Start Cloud Native Infrastructure and Services

echo Starting infrastructure services...
docker compose -f docker-compose.infrastructure.yml up -d

echo Waiting for infrastructure to be ready...
timeout /t 10 /nobreak >nul

echo Starting application services...
docker compose up -d

echo.
echo All services started!
echo.
echo Service URLs:
echo - Kong Gateway: http://localhost:8000
echo - Kong Admin: http://localhost:8001
echo - User Service: http://localhost:3001
echo - Product Service: http://localhost:3002
echo - Order Service: http://localhost:3003
echo - Prometheus: http://localhost:9090
echo - Grafana: http://localhost:3000 (admin/admin)
echo - Jaeger: http://localhost:16686
echo - Consul: http://localhost:8500
echo.
echo Run 'docker compose ps' to check status
echo Run 'check-health.bat' to verify health endpoints
