@echo off
REM Check health of all services

echo Checking service health...
echo.

echo [User Service]
curl -s http://localhost:3001/health
echo.
echo.

echo [Product Service]
curl -s http://localhost:3002/health
echo.
echo.

echo [Order Service]
curl -s http://localhost:3003/health
echo.
echo.

echo [MongoDB]
docker exec mongodb mongosh --quiet --eval "db.adminCommand('ping')" 2>nul
if %errorlevel% equ 0 (
    echo MongoDB: OK
) else (
    echo MongoDB: FAILED
)
echo.

echo [Kong Gateway]
curl -s http://localhost:8001/ >nul 2>&1
if %errorlevel% equ 0 (
    echo Kong: OK
) else (
    echo Kong: FAILED
)
echo.

echo [Prometheus]
curl -s http://localhost:9090/-/healthy
echo.
echo.

echo Done!
